"""
Crawler implementation
"""

import article
import json
import os
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from time import sleep
from constants import CRAWLER_CONFIG_PATH, PROJECT_ROOT

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'
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
    def __init__(self, seed_urls: list, max_articles: int, max_articles_per_seed: int):
        self.seed_urls = seed_urls
        self.max_articles = max_articles
        self.max_articles_per_seed = max_articles_per_seed
        self.urls = []

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
        self.full_url = full_url
        self.article_id = article_id
        self.article = article.Article(full_url, article_id)

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
        config = json.load(file)

    unknown = ('base_urls' not in config or 'total_artivles_to_find_and_parse' not in config
               or 'max_number_articles_to_get_from_one_seed' not in config)
    if not isinstance(config, dict) and unknown:
        raise UnknownConfigError

    if not isinstance(config['base_urls'], list) or \
            not (all(isinstance(url, str) for url in config['base_urls'])):
        raise IncorrectURLError

    if config['total_articles_to_find_and_parse'] < 0:
        raise IncorrectNumberOfArticlesError

    if config['max_number_articles_to_get_from_one_seed'] < 0 or \
            config['max_number_articles_to_get_from_one_seed'] > config['total_articles_to_find_and_parse']:
        raise NumberOfArticlesOutOfRangeError


if __name__ == '__main__':
    # YOUR CODE HERE
    seed_urls, max_articles, max_articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)
