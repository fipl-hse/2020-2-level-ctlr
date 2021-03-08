"""
Crawler implementation
"""

import re
import requests
from time import sleep
from bs4 import BeautifulSoup

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
    def __init__(self, seed_urls: list, max_articles=1):
        self.seed_urls = seed_urls
        self.max_articles = max_articles

    @staticmethod
    def _extract_url(article_bs):
        pass

    def find_articles(self):
        """
        Finds articles
        """
        headers = {
            'Use-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/88.0.4324.41 YaBrowser/21.2.0.1097 Yowser/2.5 Safari/537.36'}

        for url in self.seed_urls:
            response = requests.get(url, headers=headers)
            page_bs = BeautifulSoup(response.content, features='lxml')

        return page_bs

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
        self.article_header = ''
        self.article_text = ''
        self.article_author = ''

    def _fill_article_with_text(self, article_soup):
        for paragraph in article_soup.find_all(name='div', class_ = "js-pict-titles"):
            self.article_text = paragraph.text

    def _fill_article_with_meta_information(self, article_soup):
        self.article_header = article_soup.find(name='h1').text
        for inf in article_soup.find_all(name='div', class_='after-ar'):
            href_name = re.search(r'/authors/[1-9]*/', str(inf))
            self.article_author = inf.find('a', href=href_name.group(0)).text

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

    test = Crawler(['https://ugra-news.ru/',
                  'https://ugra-news.ru/article/andrey_filatov_vstupil_v_dolzhnost_glavy_surguta/'])
    bs = test.find_articles()
    test_2 = ArticleParser('https://ugra-news.ru/article/andrey_filatov_vstupil_v_dolzhnost_glavy_surguta/', 1)

    test_2._fill_article_with_meta_information(bs)
    test_2._fill_article_with_text(bs)
    print(test_2.article_author)
    print(test_2.article_text)
    print(test_2.article_header)
