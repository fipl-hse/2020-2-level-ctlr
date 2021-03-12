"""
Crawler implementation
"""
import requests
import json
import os
from time import sleep
from bs4 import BeautifulSoup
import re

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
    def __init__(self, seed_urls: list, max_articles: int, max_articles_per_seed: int):
        self.seed_urls = seed_urls
        self.max_articles = max_articles
        self.max_articles_per_seed = max_articles_per_seed
        self.urls = []

    @staticmethod
    def _extract_url(article_bs):
        return article_bs.findAll('a', attrs={'href': re.compile("/node/")})

    def find_articles(self):
        """
        Finds articles
        """

        headers = {
            'user-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36'
        }

        for url in self.seed_urls:
            response = requests.get(url, headers=headers)
            sleep(random.randrange(3,5))
            page = BeautifulSoup(response.content, features='lxml')
            links = self._extract_url(page)
            for link in links:
                link2 = re.findall(r'/node/\d{4}', str(links))

            for link_url in link2:
                code = 'http://kamtime.ru' + link_url
                if code not in self.urls and len(self.urls) < self.max_articles:
                    self.urls.append(code)

            return self.urls


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
        self.full_url = full_url
        self.article_id = article_id
        self.article = Article(full_url, article_id)


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
        pass


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if os.path.exists(base_path):
        shutil.rmtree(base_path)
    os.makedirs(base_path)


def validate_config(crawler_path):
    with open(crawler_path) as config_file:
        crawler_conf = json.load(config_file)

        if not isinstance(crawler_conf, dict):
            raise UnknownConfigError

        if not isinstance(crawler_conf['base_urls'], list):
            raise IncorrectURLError

        if not all(isinstance(url, str) for url in crawler_conf['base_urls']):
            raise IncorrectURLError

        if not isinstance(crawler_conf['total_articles_to_find_and_parse'], int):
            raise IncorrectNumberOfArticlesError

        if crawler_conf['total total_articles_to_find_and_parse'] > 100000:
            raise NumberOfArticlesOutOfRangeError

        return crawler_conf['base_urls'], crawler_conf['total_articles_to_find_and_parse'], \
            crawler_conf['max_number_articles_to_get_from_one_seed']



if __name__ == '__main__':
    pass