"""
Crawler implementation
"""
import datetime
import json
import os
import random
import re
from time import sleep
from bs4 import BeautifulSoup
import requests
import article

from constants import CRAWLER_CONFIG_PATH
from constants import PROJECT_ROOT

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'}

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
class BadStatusCode(Exception):
    """
    Custom error
    """

class Crawler:
    """
    Crawler implementation
    """

    def __init__(self, seed_urls: list, max_articles: int, max_articles_per_seed: int):
        self.seed_urls = seed_urls
        self.total_max_articles = max_articles
        self.max_articles_per_seed = max_articles_per_seed
        self.urls = []

    @staticmethod
    def _extract_url(article_bs):
        links_list = []
        soup_strings = article_bs.find_all(class_="penci-grid")
        links = re.findall(r'(\"https?://кан-чарас.рф/.+/")', str(soup_strings))
        for link in links:
            if link not in links_list:
                links_list.append(link)
        return links_list


    def find_articles(self):
        """
        Finds articles
        """
        raw_urls = []
        for url in self.seed_urls:
            response = requests.get(url, headers=headers)
            print('Making a request...')
            sleep(random.randrange(3, 6))
            articles_page = BeautifulSoup(response.content, 'lxml')
            links = self._extract_url(articles_page)
            raw_urls.extend(links)
        for url in raw_urls:
            self.urls.append(url)
        return self.urls

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        pass


class ArticleParser:
    """
    ArticleParser implementation
    """
    def __init__(self, full_url: str, article_id: int):
        pass

    def _fill_article_with_text(self, article_soup):
        pass

    def _fill_article_with_meta_information(self, article_soup):
        pass

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format
        """
        pass

    def parse(self):
        """
        Parses each article
        """
        pass


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    pass


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as file:
        conf = json.load(file)

    if not isinstance(conf, dict) or 'base_urls' not in conf or \
            'max_number_articles_to_get_from_one_seed' not in conf or 'total_articles_to_find_and_parse' not in conf:
        raise UnknownConfigError

    if not isinstance(conf['base_urls'], list) or \
            not all([isinstance(seed_url, str) for seed_url in conf['base_urls']]):
        raise IncorrectURLError

    if not isinstance(conf['total_articles_to_find_and_parse'], int) or \
            not isinstance(conf['max_number_articles_to_get_from_one_seed'], int):
        raise TypeError

    if conf['total_articles_to_find_and_parse'] < 0:
        raise IncorrectNumberOfArticlesError

    if conf['max_number_articles_to_get_from_one_seed'] < 0 or \
            conf['max_number_articles_to_get_from_one_seed'] > conf['total_articles_to_find_and_parse']:
        raise NumberOfArticlesOutOfRangeError

    return conf['base_urls'], conf['total_articles_to_find_and_parse'], conf['max_number_articles_to_get_from_one_seed']


if __name__ == '__main__':
    seed_urls, max_articles, max_articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    example = Crawler(seed_urls, max_articles, max_articles_per_seed)
    articles = example.find_articles()
    print(articles)


