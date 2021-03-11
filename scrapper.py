"""
Crawler implementation
"""

import os
import json
from datetime import date
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from time import sleep as wait
from random import randint
from article import Article
from constants import CRAWLER_CONFIG_PATH, ASSETS_PATH, LINKS_STORAGE, URL_START


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
        # print(extracted)
        # print('          ',extracted)
        return list(filter(lambda x: x.startswith('/news/')
                           and x not in seen, extracted))

    def find_articles(self):
        """
        Finds articles
        """
        for link in self.seed_urls:
            article_bs = BeautifulSoup(requests.get(link, 'html.parser').text, 'html.parser')
            newfound = self._extract_url(article_bs, self.urls)
            self.urls.extend(newfound[:self.max_articles_per_seed])
        self.urls = [i for i in self.urls if len(i) > 20
                     and not any(map(lambda y: y.isupper(), i))][:self.total_max_articles]
        print('Scraped seed urls, overall number of urls is', len(self.urls))
        old = len(self.urls)
        while len(self.urls) < self.total_max_articles:
            print('Due to insufficient number started further iteration')
            print('current number', len(self.urls), ', required', self.total_max_articles)
            for link in self.urls:
                article_bs = BeautifulSoup(requests.get(URL_START + link, 'html.parser').text, 'html.parser')
                newfound = list(filter(lambda x: len(x) > 20, self._extract_url(article_bs, self.urls)))
                print('    checked new url, found', len(newfound), 'articles')
                self.urls.extend(newfound[:self.max_articles_per_seed])
                # wait(10)
                if len(self.urls) > self.total_max_articles:
                    break
            if len(self.urls) == old:
                print('     Something is wrong with scraping parameters')
                break

            self.urls = self.urls[:self.total_max_articles]


class CrawlerRecursive(Crawler):

    def __init__(self, seed_urls: list, total_max_articles: int, max_articles_per_seed: int):
        super().__init__(seed_urls, total_max_articles, max_articles_per_seed)

    def find_articles(self):
        if self.get_backedup():
            print('backed up urls found, starting iteration')
        if not self.urls:
            for link in self.seed_urls:
                # wait(randint(0, 10))
                article_bs = BeautifulSoup(requests.get(link, 'html.parser').text, 'html.parser')
                newfound = self._extract_url(article_bs, self.urls)
                self.urls.extend(newfound)
                self.urls = [i for i in self.urls if len(i) > 20
                             and not any(map(lambda y: y.isupper(), i))]
                with open('links/url_backup.txt', 'w', encoding='utf-8') as file:
                    file.write('\n'.join(self.urls))
            print(f'Scraped {len(self.urls)} from seed')
            if self.verify_proceed():
                print('starting recursive scraping')
                self.find_articles()
            else:
                print(f'recursive crawling finished with {len(self.urls)} urls.')
        else:
            old = len(self.urls)
            for link in self.urls:
                # wait(randint(0, 10))
                article_bs = BeautifulSoup(requests.get(URL_START + link, 'html.parser').text, 'html.parser')
                newfound = self._extract_url(article_bs, self.urls)
                newfound = [i for i in newfound if len(i) > 20
                            and not any(map(lambda y: y.isupper(), i))]
                self.urls.extend(newfound)
            with open('links/url_backup.txt', 'a', encoding='utf-8') as file:
                file.write('\n'.join(self.urls))
            if len(self.urls) == old:
                print(f'there are no unseen links found\nrecursive crawling finished with {len(self.urls)} urls.')
            else:
                print(f'found {len(self.urls) - old} new urls')
                if self.verify_proceed():
                    print('starting new iteration')
                    self.find_articles()
                else:
                    print(f'recursive crawling finished with {len(self.urls)} urls.')

    @staticmethod
    def verify_proceed():
        answer = input('Would you like to proceed? yes or no: ').strip()
        return True if answer == 'yes' else False

    def get_backedup(self):
        try:
            with open('links/url_backup.txt', 'r', encoding='utf-8') as file:
                sources = file.read().split('\n')
                self.urls = sources
                return True
        except FileNotFoundError:
            return False

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.urls


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
            text = article_soup.find('div', {'class': 'text letter', 'itemprop': 'articleBody'}).text.strip()
            self.article.text = text
        except AttributeError:
            print('    unable to parse', self.full_url)

    def _fill_article_with_meta_information(self, article_soup):
        try:
            title = article_soup.title.text
            self.article.title = title

            credit = article_soup.find('div', {'class': 'credits t-caption'}).text.strip().split('\n')[0]
            if 'Автор:' in credit:
                author = article_soup.find('div', {'class': 'credits t-caption'}).text.strip().split('\n')[0][7:]
            elif 'Источник:' in credit:
                author = article_soup.find('div', {'class': 'credits t-caption'}).text.strip()
                author = author.split('\n')[0][9:].strip()
            else:
                author = ''
            self.article.author = author
            when = article_soup.find('div', {'class': 'b-caption'}).text.strip().split('\n')[1]
            self.article.date = self.unify_date_format(when)

            topic = article_soup.find('div', {'class': 'b-caption'}).text.strip().split('\n')[0]
            self.article.topics = topic
        except AttributeError:
            print('    something is off with', self.full_url)
        # print(title)
        # self.article.title = title

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
        # print(self.full_url)
        self.article.url = self.full_url
        self.article.article_id = self.article_id
        html = requests.get(self.full_url, 'html.parser').text
        article_bs = BeautifulSoup(html, 'html.parser')
        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        self.article.save_raw()


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if not os.path.exists(base_path):
        os.makedirs(base_path)


def enable_backup(base_path):
    """
    Creates folder for backup links if not created
    """
    if not os.path.exists(base_path):
        os.makedirs(base_path)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as crawler_config:
        config = json.load(crawler_config)
    try:
        good_response = list(map(lambda link: requests.get(link).status_code == 200,
                                 config['base_urls']))
    except RequestException as exception:
        raise IncorrectURLError from exception
    except Exception as exception:
        raise UnknownConfigError from exception
    if not all(good_response):
        raise IncorrectURLError
    try:
        if not isinstance(config['total_articles_to_find_and_parse'], int):
            raise IncorrectNumberOfArticlesError
        if config['total_articles_to_find_and_parse'] > 1000:
            raise NumberOfArticlesOutOfRangeError
        # if not isinstance(config['max_number_articles_to_get_from_one_seed'], int):
        #     raise IncorrectNumberOfArticlesError
        # if not config['total_articles_to_find_and_parse'] < config['max_number_articles_to_get_from_one_seed']\
        #    * len(good_response):
        #     raise NumberOfArticlesOutOfRangeError
    except KeyError as exception:
        raise IncorrectNumberOfArticlesError from exception
    try:
        return config['base_urls'], config['total_articles_to_find_and_parse'], \
            config['max_number_articles_to_get_from_one_seed']
    except KeyError:
        return config['base_urls'], config['total_articles_to_find_and_parse'], None


if __name__ == '__main__':
    prepare_environment(ASSETS_PATH)
    enable_backup(LINKS_STORAGE)
    seedurls, max_articles, max_arts_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    if not max_arts_per_seed:
        max_arts_per_seed = max_articles
    crawler = CrawlerRecursive(seed_urls=seedurls,
                               total_max_articles=max_articles,
                               max_articles_per_seed=max_arts_per_seed)

    crawler.find_articles()
    # print('Scraped', len(crawler.urls), 'articles')

    print('onto parsing')

    for n, url in enumerate(crawler.urls):
        full_url = URL_START + url
        parser = ArticleParser(full_url, n + 1)
        parser.parse()
    print('parsing is finished')
