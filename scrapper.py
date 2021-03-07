"""
Crawler implementation
"""
import requests
from bs4 import BeautifulSoup
from constants import CRAWLER_CONFIG_PATH
import json


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
        pass

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


def validate_config(crawler_path): # возможна замена значений в условиях
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as f:
        initial_values = json.load(f)

    for url in initial_values["base_urls"]:
        if not isinstance(url, str):
            raise IncorrectURLError

    if initial_values["base_urls"] == []:
        raise IncorrectURLError

    if initial_values["total_articles_to_find_and_parse"] <= 0 \
            or initial_values["total_articles_to_find_and_parse"] > 100:
        raise NumberOfArticlesOutOfRangeError

    if initial_values["max_number_articles_to_get_from_one_seed"] > initial_values["total_articles_to_find_and_parse"] \
            or initial_values["max_number_articles_to_get_from_one_seed"] <= 0:
        raise IncorrectNumberOfArticlesError

    if not isinstance(initial_values["total_articles_to_find_and_parse"], int) \
        or not isinstance(initial_values["max_number_articles_to_get_from_one_seed"], int):
        raise UnknownConfigError

    return initial_values["base_urls"], initial_values["total_articles_to_find_and_parse"], \
               initial_values["max_number_articles_to_get_from_one_seed"]


if __name__ == '__main__':
    # YOUR CODE HERE
    seed_urls, max_articles, max_articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    print(seed_urls, max_articles, max_articles_per_seed)