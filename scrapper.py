"""
Crawler implementation
"""
import json
import os
from time import sleep
import datetime
import random
import shutil
import requests
from bs4 import BeautifulSoup
import article
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
headers={
        'user-agent':
    'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/88.0.4324.152 YaBrowser/21.2.2.102 Yowser/2.5 Safari/537.36'}

class Crawler:
    """
    Crawler implementation
    """
    def __init__(self, seed_urls: list, max_articles: int,max_articles_per_seed:int):
        self.seed_urls = seed_urls
        self.total_max_articles = max_articles
        self.max_articles_per_seed = max_articles_per_seed
        self.urls = []

    @staticmethod
    def _extract_url(article_bs):
        links_page=[]
        for tag in article_bs.find_all(class_='next news'):
            links_page.append(tag.find('a').get('href'))
        return links_page

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
    pass


if __name__ == '__main__':
    # YOUR CODE HERE
    pass
