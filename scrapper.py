"""
Crawler implementation
"""
import json

import requests
from bs4 import BeautifulSoup
from time import sleep
import random
from constants import PROJECT_ROOT
from constants import ASSETS_PATH
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


class UnknownConfigError(Exception):
    """
    Most general error
    """


class Crawler:
    """
    Crawler implementation
    """

    def __init__(self, seed_urls: list, max_articles: int):
        self.seed_urls = seed_urls
        self.max_articles = max_articles
        self.headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML,'
                                      ' like Gecko) Chrome/88.0.4324.150 Safari/537.36'}

    @staticmethod
    def _extract_url(self, article_bs):
        responsee = requests.get(article_bs, headers=self.headers)
        return responsee

    def find_articles(self):
        """
        Finds articles
        """
        page_content = self._extract_url().content
        page_soup = BeautifulSoup(page_content, features='lxml')
        div_tag = page_soup.find('div', class_='news-list')
        urls = []
        for link in div_tag.find_all('a'):
            urls.append(link.get('href'))
        urls = urls[1:10:2]
        return urls[:self.max_articles]

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        seed_urls = []
        urls = self.find_articles()
        for url in urls:
            seed_urls.append('https://восход65.рф' + url)
            print(seed_urls.append('https://восход65.рф' + url))
        return seed_urls


crawler = Crawler(["https://xn--65-dlci3cau6a.xn--p1ai/news/events/"], 5)



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
    with open(crawler_path, 'r', encoding='utf-8') as conf_file:
        conf = json.load(conf_file)

    max_n_articles = "max_number_articles_to_get_from_one_seed"
    total_art = "total_articles_to_find_and_parse"

    if not isinstance(conf, dict) or \
            "base_urls" not in conf or total_art not in conf \
            or max_n_articles not in conf:
        raise UnknownConfigError

    if not isinstance(conf["base_urls"], list) or \
            not (isinstance(url, str) for url in conf["base_urls"]):
        raise IncorrectURLError

    if conf[max_n_articles] > conf[total_art]:
        raise NumberOfArticlesOutOfRangeError

    if not isinstance(conf[max_n_articles], int) or conf[max_n_articles] < 0 \
            or conf[total_art] < 0:
        raise IncorrectNumberOfArticlesError


seed_urls, max_articles, max_articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)

if __name__ == '__main__':
    # YOUR CODE HERE
    pass
