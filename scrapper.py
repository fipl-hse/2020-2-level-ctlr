"""
Crawler implementation
"""

import os
import re
import json
from datetime import date
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
# from time import sleep as wait
from article import Article

CRAWLER_CONFIG_PATH = 'crawler_config.json'
NEWLINES_RE = re.compile(r"\n{2,}")  # two or more "\n" characters


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

        self.URLSTART = 'https://burunen.ru'

    @staticmethod
    def _extract_url(article_bs, seen):
        extracted = list(set([link['href'] for link in article_bs.find_all('a', href=True)]))
        # print(extracted)
        # print('          ',extracted)
        return list(filter(lambda x: True if x.startswith('/news/')
                           and x not in seen
                           # and any(map(lambda y: y.isdigit(), x))
                           else False, extracted))

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
                article_bs = BeautifulSoup(requests.get(self.URLSTART + link, 'html.parser').text, 'html.parser')
                newfound = filter(lambda x: len(x) > 20, self._extract_url(article_bs, self.urls))
                print('    checked new url, found', len(newfound), 'articles')
                self.urls.extend(newfound[:self.max_articles_per_seed])
                # wait(10)
                if len(self.urls) > self.total_max_articles:
                    break
            if len(self.urls) == old:
                print('     Something is wrong with scraping parameters')
                break

            self.urls = self.urls[:self.total_max_articles]

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
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
            text = article_soup.find('div', {'class': 'text letter', 'itemprop': 'articleBody'}).text.strip()
            # text = NEWLINES_RE.split(all_text)  # regex splitting
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
    newpath = r'{}/ASSETS_PATH'.format(base_path)
    if not os.path.exists(newpath):
        os.makedirs(newpath)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as crawler_config:
        config = json.load(crawler_config)
    try:
        good_response = list(map(lambda link: True if requests.get(link).status_code == 200 else False,
                                 config['base_urls']))
    except RequestException as e:
        raise IncorrectURLError from e
    except Exception as e:
        raise UnknownConfigError from e
    if not all(good_response):
        raise IncorrectURLError
    if not all((isinstance(config['total_articles_to_find_and_parse'], int),
                isinstance(config['max_number_articles_to_get_from_one_seed'], int))):
        raise IncorrectNumberOfArticlesError
    if not config['total_articles_to_find_and_parse'] < config['max_number_articles_to_get_from_one_seed']\
       * len(good_response):
        raise NumberOfArticlesOutOfRangeError
    return config['base_urls'], config['total_articles_to_find_and_parse'], \
        config['max_number_articles_to_get_from_one_seed']


if __name__ == '__main__':
    seedurls, max_articles, max_arts_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    crawler = Crawler(seed_urls=seedurls,
                      total_max_articles=max_articles,
                      max_articles_per_seed=max_arts_per_seed)

    crawler.find_articles()
    # print('Scraped', len(crawler.urls), 'articles')

    print('onto parsing')

    for n, url in enumerate(crawler.urls):
        full_url = crawler.URLSTART + url
        parser = ArticleParser(full_url, n + 1)
        parser.parse()
    print('parsing is finished')
