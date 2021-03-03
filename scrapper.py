"""
Crawler implementation
"""
import json
import requests
import random
import re
from constants import CRAWLER_CONFIG_PATH
from time import sleep
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'}

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
    Custom error
    """


class Crawler:
    """
    Crawler implementation
    """
    def __init__(self, seed_urls: list, max_articles: int, max_articles_per_seed: int):
        self.seed_urls = seed_urls
        self.total_max_articles = max_articles
        self.max_articles_per_seed = max_articles_per_seed
        self.urls = []

    @staticmethod
    def _extract_url(article_bs):
        pass

    def find_articles(self):
        """
        Finds articles
        """
        raw_urls_list = []
        for url in self.seed_urls:
            response = requests.get(url, headers=headers)
            print('Making a request...')
            sleep_interval = random.randrange(2, 5)
            sleep(sleep_interval)
            text = response.text
            link_sample = re.compile(r'<h3><a href="/\d{6}.+"')
            raw_urls_list.extend(re.findall(link_sample, text))
        for url in raw_urls_list:
            self.urls.append(url.replace('<h3><a href="', 'https://www.infpol.ru')[:-1])


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
    with open(crawler_path, 'r') as crawler:
        data = json.loads(str(crawler.read()))
        validating_seed_urls = data["base_urls"]
        validating_max_articles = data["total_articles_to_find_and_parse"]
        validating_max_articles_per_seed = data["max_number_articles_to_get_from_one_seed"]

    if not isinstance(validating_seed_urls, list) or not isinstance(validating_max_articles, int)\
            or not isinstance(validating_max_articles_per_seed, int):
        raise UnknownConfigError

    for url in validating_seed_urls:
        response = requests.get(url)
        if not response:
            raise IncorrectURLError

    '''if validating_max_articles == 0:
        raise NumberOfArticlesOutOfRangeError

    if validating_max_articles_per_seed == 0:
        raise IncorrectNumberOfArticlesError'''
    return validating_seed_urls, validating_max_articles, validating_max_articles_per_seed


if __name__ == '__main__':
    seed_urls, max_articles, max_articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    example = Crawler(seed_urls, max_articles, max_articles_per_seed)
    example.find_articles()
    pass
