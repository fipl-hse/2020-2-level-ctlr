import requests
import json
import re
from time import sleep
from bs4 import BeautifulSoup
from constants import CRAWLER_CONFIG_PATH

headers = {
        'user-agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/88.0.4324.111 YaBrowser/21.2.1.108 Yowser/2.5 Safari/537.36'

}


"""
Crawler implementation
"""


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
        url_article = article_bs.find(id="MainMasterContentPlaceHolder_DefaultContentPlaceHolder_ctl02_ctl00_articleHeader").find('a')
        return url_article.attr(['href'])

    def find_articles(self):
        """
        Finds articles
        """
        for url in self.seed_urls:
            response = requests.get(url, headers=headers)
            sleep(5)
            if not response:
                raise IncorrectURLError




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
    with open(crawler_path) as crawler:
        crawler_config = json.load(crawler)

    for url in crawler_config['base_urls']:
        if not re.match('https://', url):
            raise IncorrectURLError

    if crawler_config['total_articles_to_find_and_parse'] > 100:
        raise NumberOfArticlesOutOfRangeError

    if not isinstance(crawler_config['total_articles_to_find_and_parse'], int):
        raise IncorrectNumberOfArticlesError

    return crawler_config['base_urls'], crawler_config['total_articles_to_find_and_parse']



if __name__ == '__main__':
    # YOUR CODE HERE