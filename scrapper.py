"""
Crawler implementation
"""
import requests

class IncorrectURLError(Exception):
    """
    Custom error
    """
    pass
    # def __init__(self, ):


class NumberOfArticlesOutOfRangeError(Exception):
    """
    Custom error
    """
    pass

class IncorrectNumberOfArticlesError(Exception):
    """
    Custom error
    """
    pass

class Crawler:
    """
    Crawler implementation
    """
    def __init__(self, seed_urls: list, max_articles: int):
        self.seed_urls = seed_urls
        self.max_articles = max_articles

    @staticmethod
    def _extract_url(article_bs):
        pass

    def find_articles(self):
        """
        Finds articles
        """
        raise IncorrectURLError



    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return seed_urls


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
    pass


if __name__ == '__main__':
    # YOUR CODE HERE
    pass
