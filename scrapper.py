"""
Crawler implementation
"""
import os

import requests
import json
import BeautifulSoup as bs4
from constants import CRAWLER_CONFIG_PATH, PROJECT_ROOT


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

    def __init__(self, seed_urls: list, max_articles: int, max_articles_per_seed: int):
        self.seed_urls = seed_urls
        self.max_articles = max_articles
        self.max_articles_per_seed = max_articles_per_seed
        self.visited_urls: set = set()
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


class CrawlerRecursive(Crawler):
    """
    Recursive Crawler
    """


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
    if not os.path.exists(os.path.join(PROJECT_ROOT, 'tmp', 'pages')):
        os.makedirs(os.path.join(PROJECT_ROOT, 'tmp', 'pages'))

    if not os.path.exists(os.path.join(base_path, 'tmp', 'articles')):
        os.makedirs(os.path.join(base_path, 'tmp', 'articles'))


def validate_config(crawler_path: str):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        config: dict = json.load(file)

    checks = {
        all(isinstance(x, str) for x in config['base_urls']): IncorrectURLError,
        (isinstance(config['total_articles_to_find_and_parse'], int) and
         config['total_articles_to_find_and_parse'] > 0): IncorrectNumberOfArticlesError,
        config['total_articles_to_find_and_parse'] <= 10000: NumberOfArticlesOutOfRangeError
    }

    for check, exception in checks.items():
        if check:
            raise exception

    if all(checks):
        return config.values()

    raise UnknownConfigError


if __name__ == '__main__':
    prepare_environment(PROJECT_ROOT)

    try:
        urls, articles, articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    except (
            IncorrectURLError,
            IncorrectNumberOfArticlesError,
            NumberOfArticlesOutOfRangeError,
            UnknownConfigError
    ) as e:
        print(f'{e} was encountered during the crawler execution')
    else:
        crawler = CrawlerRecursive(
            seed_urls=urls,
            max_articles=articles,
            max_articles_per_seed=articles_per_seed
        )

        crawler.find_articles()



