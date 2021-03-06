"""
Crawler implementation
"""
import requests
import json
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
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                             '(KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'}

    def __init__(self, seed_urls: list, max_articles: int):
        self.seed_urls = seed_urls
        self.max_articles = max_articles
        self.visited_urls: list = []
        self.urls: list = []

    @staticmethod
    def _extract_url(article_bs):
        pass

    def find_articles(self):
        """
        Finds articles
        """
        pass

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


def validate_config(crawler_path: str):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        config: dict = json.load(file)

    params: tuple = 'base_urls', 'total_articles_to_find_and_parse', 'max_number_articles_to_get_from_one_seed'

    if not all((isinstance(config, dict), params == config.keys())):
        print('UnknownConfigError 1')
        raise UnknownConfigError
    
    type_checks = [
        # all([isinstance(x, str) for x in config['base_url']]),
        isinstance(config['total_articles_to_find_and_parse'], int),
        isinstance(config['max_number_articles_to_get_from_one'], int)
    ]

    if not type_checks:
        print('UnknownConfigError 2')
        raise UnknownConfigError

    if not all(isinstance(x, str) for x in config['base_url']):
        print('IncorrectURLError')
        raise IncorrectURLError

    if config['total_articles_to_find_and_parse'] < 0:
        print('IncorrectNumberOfArticlesError')
        raise IncorrectNumberOfArticlesError

    if not config['max_number_articles_to_get_from_one_seed'] < config['total_articles_to_find_and_parse'] < 10000:
        print('NumberOfArticlesOutOfRangeError')
        raise NumberOfArticlesOutOfRangeError

    return config.values()


if __name__ == '__main__':
    pass
