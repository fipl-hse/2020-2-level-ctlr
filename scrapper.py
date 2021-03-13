"""
Crawler implementation
"""

from datetime import date
import json
import os
from random import randint
from time import sleep as wait

from bs4 import BeautifulSoup
import requests
from requests.exceptions import RequestException

from article import Article
from constants import CRAWLER_CONFIG_PATH, ASSETS_PATH, LINKS_STORAGE_DIR, URL_START, HEADERS, LINKS_STORAGE_FILE


class IncorrectURLError(Exception):
    """
    Custom error
    """


class NumberOfArticlesOutOfRangeError(Exception):
    """
    Custom error
    """


class IncorrectNumberOfArticlesError(Exception):
    """
    Custom error
    """


class UnknownConfigError(Exception):
    """
    Most general error
    """


class NoBackUpEnabled(Exception):
    """
    Custom Error
    """


class Crawler:
    """
    Crawler implementation
    """
    def __init__(self, seed_urls: list, total_max_articles: int, max_articles_per_seed: int):
        self.seed_urls = seed_urls
        self.total_max_articles = total_max_articles
        self.max_articles_per_seed = max_articles_per_seed
        self.urls = []

    @staticmethod
    def _extract_url(article_bs, seen):
        extracted = list({link['href'] for link in article_bs.find_all('a', href=True)})
        return list(filter(lambda x: x.startswith('/news/')
                           and x not in seen, extracted))

    def find_articles(self):
        """
        Finds articles
        """
        for link in self.seed_urls:
            article_bs = BeautifulSoup(requests.get(link, 'html.parser', headers=HEADERS).text, 'html.parser')
            newfound = self._extract_url(article_bs, self.urls)
            self.urls.extend(newfound[:self.max_articles_per_seed])
        self.urls = [i for i in self.urls if len(i) > 20
                     and not any(map(lambda y: y.isupper(), i))][:self.total_max_articles]
        print('Scraped seed urls, overall number of urls is', len(self.urls))
        while len(self.urls) < self.total_max_articles:
            print('Due to insufficient number started further iteration')
            print('current number', len(self.urls), ', required', self.total_max_articles)
            old = len(self.urls)
            for link in self.urls:
                article_bs = BeautifulSoup(requests.get(URL_START + link,
                                                        'html.parser', headers=HEADERS).text, 'html.parser')
                newfound = list(filter(lambda x: len(x) > 20, self._extract_url(article_bs, self.urls)))
                print('checked new url, found', len(newfound), 'articles')
                self.urls.extend(newfound[:self.max_articles_per_seed])
                if len(self.urls) > self.total_max_articles:
                    break
            if len(self.urls) == old:
                print('There are no unseen urls found in all of the available addresses')
                print(f'crawling finished with {len(self.urls)}')
                break
            self.urls = self.urls[:self.total_max_articles]

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.urls


class CrawlerRecursive(Crawler):

    def __init__(self, seed_urls: list, total_max_articles: int, max_articles_per_seed: int, to_wait=False):
        super().__init__(seed_urls, total_max_articles, max_articles_per_seed)
        self.is_waiting = to_wait

    def _crawl(self, pool: list):
        found = []
        for link in pool:
            if self.is_waiting:
                wait(randint(0, 10))
            article_bs = BeautifulSoup(requests.get(URL_START + link, headers=HEADERS).text, 'html.parser')
            newfound = self._extract_url(article_bs, self.urls)
            newfound = [i for i in newfound if len(i) > 20
                        and not any(map(lambda y: y.isupper(), i))]
            found.extend(newfound)
        return list(set(found))

    def find_articles(self):
        if self.read_backedup():
            print('backed up urls found, starting iteration')
        if not self.urls:
            pool = self.seed_urls
        else:
            pool = self.urls
        newfound = self._crawl(pool)
        if not newfound:
            print(f'there are no unseen links found\nrecursive crawling finished with {len(self.urls)} urls.')
        else:
            self.urls.extend(newfound)
            with open(LINKS_STORAGE_FILE, 'a', encoding='utf-8') as file:
                file.write('\n'.join(newfound))
            print(f'found {len(newfound)} new urls')
            if self.verify_proceed():
                print('starting new iteration')
                self.find_articles()
            else:
                print(f'recursive crawling finished with {len(self.urls)} urls.')

    @staticmethod
    def verify_proceed():
        answer = input('Would you like to proceed? yes or no: ').strip()
        return answer == 'yes'

    def read_backedup(self):
        try:
            with open(LINKS_STORAGE_FILE, 'r', encoding='utf-8') as file:
                sources = file.read().split('\n')
                self.urls = sources
                if self.urls:
                    print('backed up urls found')
        except FileNotFoundError:
            print('no backed up files found')
            with open(LINKS_STORAGE_FILE, 'w', encoding='utf-8'):
                pass


class ArticleParser:
    """
    ArticleParser implementation
    """
    def __init__(self, full__url: str, article_id: int):
        self.full_url = full__url
        self.article_id = article_id
        self.article = Article(self.full_url, self.article_id)

    def _fill_article_with_text(self, article_soup):
        try:
            text = article_soup.find('div', {'class': 'text letter',
                                             'itemprop': 'articleBody'}).text.strip().split('\n')
            stopws = ['Фото:', 'Автор:', 'Источник:',  '© фото:']
            self.article.text = ' '.join(filter(lambda line:
                                         all(map(lambda stopw: stopw not in line, stopws)), text)).strip()
        except AttributeError:
            print('unable to parse', self.full_url)
            self.article.text = 'ERROR'

    def _fill_article_with_meta_information(self, article_soup):
        try:
            title = article_soup.title.text
            self.article.title = title
            author = article_soup.find('div',
                                       {'class': 'credits t-caption'}).text.strip().split('\n')[0].split(': ')[-1]
            self.article.author = author.strip()
            when = article_soup.find('div', {'class': 'b-caption'}).text.strip().split('\n')[1]
            self.article.date = self.unify_date_format(when)
            topic = article_soup.find('div', {'class': 'b-caption'}).text.strip().split('\n')[0]
            self.article.topics = topic
        except AttributeError:
            print('something is off with', self.full_url)

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format
        """
        day, month, year = date_str.split()
        if len(day) == 1:
            day = '0' + day
        match = {'янв': '01',
                 'фев': '02',
                 'мар': '03',
                 'апр': '04',
                 'май': '05',
                 'июн': '06',
                 'июл': '07',
                 'авг': '08',
                 'сен': '09',
                 'окт': '10',
                 'ноя': '11',
                 'дек': '12'}
        return date.fromisoformat(year + '-' + match[month] + '-' + day)

    def parse(self):
        """
        Parses each article
        """
        html = requests.get(self.full_url, 'html.parser', headers=HEADERS).text
        article_bs = BeautifulSoup(html, 'html.parser')
        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        return self.article


def prepare_environment(base_path, backup_path_dir):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    if not os.path.exists(backup_path_dir):
        print('GOT HERE WITH PATH', backup_path_dir)
        os.makedirs(backup_path_dir)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as crawler_config:
        config = json.load(crawler_config)
    good_response = list(map(lambda link: link.startswith('https://'),
                             config['base_urls']))
    if not all(good_response):
        raise IncorrectURLError
    try:
        if not isinstance(config['total_articles_to_find_and_parse'], int):
            raise IncorrectNumberOfArticlesError
        if config['total_articles_to_find_and_parse'] > 1000:
            raise NumberOfArticlesOutOfRangeError
    except KeyError as exception:
        raise IncorrectNumberOfArticlesError from exception
    try:
        return config['base_urls'], config['total_articles_to_find_and_parse'], \
            config['max_number_articles_to_get_from_one_seed']
    except KeyError:
        return config['base_urls'], config['total_articles_to_find_and_parse'], None


if __name__ == '__main__':
    prepare_environment(ASSETS_PATH, LINKS_STORAGE_DIR)
    seedurls, max_articles, max_arts_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    if not max_arts_per_seed:
        max_arts_per_seed = max_articles
    crawler = Crawler(seed_urls=seedurls,
                      total_max_articles=max_articles,
                      max_articles_per_seed=max_arts_per_seed)

    crawler.find_articles()

    print('onto parsing')

    for n, url in enumerate(crawler.urls[:4]):
        full_url = URL_START + url
        parser = ArticleParser(full_url, n + 1)
        article = parser.parse()
        article.save_raw()
    print('parsing is finished')
#
