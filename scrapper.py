"""
Crawler implementation
"""
from bs4 import BeautifulStoneSoup
from constants import CRAWLER_CONFIG_PATH
from time import sleep
import json
import requests


headers = {
        'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'
}

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
        self.url = []

    @staticmethod
    def _extract_url(article_bs):
        pass

    def find_articles(self):
        """
        Finds articles
        """
        url_list = []
        for url in self.seed_urls:
            response = requests.get(url, headers=headers)
        '''
        for url in self.seed_urls:
            sleep(5)
            print('made requests')
        '''

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
    with open(crawler_path, 'r') as file:
        crawler = json.load(file)
    all_urls = crawler.get('base_urls')

    for link in all_urls:
        link = type(link, str)

    articles_to_find_and_parse = crawler.get('total_articles_to_find_and_parse')
    articles = type(articles_to_find_and_parse, int)
    max_number_of_articles = crawler.get('max_number_articles_to_get_from_one_seed')
    max_number_of_art = type(max_number_of_articles, int)

    for link in all_urls:
        if link != type(str):
            raise IncorrectURLError


    if not isinstance(articles, int)\
        or not isinstance(max_number_of_art, int):
        raise NumberOfArticlesOutOfRangeError


    if articles < max_number_of_art:
        raise IncorrectNumberOfArticlesError



if __name__ == '__main__':
    # YOUR CODE HERE
    response = requests.get('https://www.ks87.ru/')
    if not requests:
        raise ImportError
    print(response.headers)