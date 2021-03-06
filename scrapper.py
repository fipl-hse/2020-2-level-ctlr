"""
Crawler implementation
"""

import json
import requests
import bs4

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


class UnknownConfigError (Exception):
    """
    Custom error
    """


class Crawler:
    """
    Crawler implementation
    """
    def __init__(self, seed_urls: list, total_max_articles: int, max_articles_per_seed):
        self.seed_urls = seed_urls
        self.max_articles = max_articles
        self.max_articles_per_seed = max_articles_per_seed

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


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as f:
        config = json.load(f)

    urls = config['base_urls']
    total_artcls = config['total_articles_to_find_and_parse']
    max_artcls = config['max_number_articles_to_get_from_one_seed']

    if (not isinstance(config, dict) or 'base_urls' not in config or 'total_articles_to_find_and_parse' not in config
            or 'max_number_articles_to_get_from_one_seed' not in config):
        raise UnknownConfigError

    if not isinstance(urls, list) or not all(isinstance(url, str) for url in urls):
        raise IncorrectURLError

    if (not isinstance(total_artcls, int) or isinstance(total_artcls, bool) or not isinstance(max_artcls, int)
            or isinstance(max_artcls, bool)):
        raise IncorrectNumberOfArticlesError

    if total_artcls < 2 or total_artcls != max_artcls:
        raise NumberOfArticlesOutOfRangeError

    return urls, total_artcls, max_artcls


if __name__ == '__main__':
    # YOUR CODE HERE
    seed_urls, max_articles, max_articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    crawler = Crawler(seed_urls=seed_urls,
                      total_max_articles=max_articles,
                      max_articles_per_seed=max_articles_per_seed)
