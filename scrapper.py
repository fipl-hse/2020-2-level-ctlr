"""
Crawler implementation
"""
import requests
import json
import os
from time import sleep
from bs4 import BeautifulSoup

from constants import CRAWLER_CONFIG_PATH

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
    def __init__(self, seed_urls: list, max_articles: int):
        self.seed_urls = seed_urls
        self.max_articles = max_articles
        self.max_articles_per_seed = max_articles_per_seed
        self.urls = []

    @staticmethod
    def _extract_url(article_bs):
        pass


    def find_articles(self):

        lst_urls = []
        headers = {
            'user-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36'
        }
        for url in self.seed_urls:
            response = requests.get(url, headers=headers)
            sleep(random.randrange(3,5))
            page = BeautifulSoup(response.content, features='lxml')
            page_links = self._extract_url(page)
            lst_urls.extend(page_links)


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
        pass


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    pass


def validate_config(crawler_path):
    with open(crawler_path) as config_file:
        crawler = json.load(crawler_file)

        if not isinstance(crawler, dict):
            raise UnknownConfigError

        if not isinstance(crawler['base_urls'], list):
            raise IncorrectURLError

        if not all(isinstance(url, str) for url in crawler['base_urls']):
            raise IncorrectURLError

        if not isinstance(crawler['total_articles_to_find_and_parse'], int):
            raise IncorrectNumberOfArticlesError

        if config_file['total total_articles_to_find_and_parse'] > 100000:
            raise NumberOfArticlesOutOfRangeError



if __name__ == '__main__':
    pass