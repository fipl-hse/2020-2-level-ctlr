"""
Crawler implementation
"""
import requests
import json
from time import sleep
import random
from bs4 import BeautifulSoup
import re

headers = {
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 YaBrowser/21.2.2.102 Yowser/2.5 Safari/537.36'
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
        url_article = article_bs.find('div', class_='entry-title').find('a')
        link = url_article.attrs['href']
        return 'https://севернаяправда.рф/' + link

    def find_articles(self):
        """
        Finds articles
        """
        for urls in self.seed_urls:
            response = requests.get(urls, headers=headers)
            sleep(random.randrange(3, 6))
            if not response:
                raise IncorrectURLError
            soup = BeautifulSoup(response.content, features='lxml')
            links = self._extract_url(soup)
            if len(links) < self.max_articles_per_seed:
                self.urls.extend(links)
            else:
                self.urls.extend(links[:self.max_articles_per_seed])


    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.seed_urls


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
    with open(crawler_path, 'r', encoding='utf-8') as file:
        configuration = json.load(file)
    if not isinstance(configuration, dict):
        raise UnknownConfigError
    if not isinstance(configuration['base_urls'], list):
        raise IncorrectURLError
    if not all(isinstance(url, str) for url in configuration['base_urls']):
        raise IncorrectURLError
    if not isinstance(configuration['total_articles_to_find_and_parse'], int):
        raise IncorrectNumberOfArticlesError
    if configuration['total_articles_to_find_and_parse'] > 100:
        raise NumberOfArticlesOutOfRangeError






if __name__ == '__main__':
    # YOUR CODE HERE
    pass
