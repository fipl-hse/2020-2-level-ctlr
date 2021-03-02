"""
Crawler implementation
"""
import re
import requests
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


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r') as crawler_config_file:
        crawler_config = json.load(crawler_config_file)

    if not isinstance(crawler_config, dict) or \
            ("base_urls" not in crawler_config or "total_articles_to_find_and_parse" not in crawler_config
             or "max_number_articles_to_get_from_one_seed" not in crawler_config):
        raise UnknownConfigError

    for key, value in crawler_config.items():
        if key == "base_urls":
            for el in value:
                if not re.fullmatch(r'https?\:\/\/.+', el):
                    raise IncorrectURLError

        if key == "total_articles_to_find_and_parse" or key == "max_number_articles_to_get_from_one_seed":
            if not isinstance(value, int):
                raise IncorrectNumberOfArticlesError

    if crawler_config["max_number_articles_to_get_from_one_seed"] > crawler_config["total_articles_to_find_and_parse"]:
        raise NumberOfArticlesOutOfRangeError

    return (crawler_config["base_urls"], crawler_config["total_articles_to_find_and_parse"],
            crawler_config["max_number_articles_to_get_from_one_seed"])


if __name__ == '__main__':
    # YOUR CODE HERE
    import constants
    seed_urls, max_articles, max_articles_per_seed = validate_config(constants.CRAWLER_CONFIG_PATH)
