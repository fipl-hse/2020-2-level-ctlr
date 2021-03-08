"""
Crawler implementation
"""

import requests
import json
from bs4 import BeautifulSoup
from time import sleep
import random


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
        url = article_bs.contents[1]
        return url.get('href')

    def find_articles(self):
        """
        Finds articles
        """
        for seed in self.seed_urls:
            sleep(random.randint(4, 8))
            headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                         'Chrome/88.0.4324.111 YaBrowser/21.2.1.108 Yowser/2.5 Safari/537.36'}
            response = requests.get(seed, headers=headers)
            if not response:
                break
            seed_soup = BeautifulSoup(response.content, features='lxml')
            article_soup = seed_soup.find_all(['li'])
            for element in article_soup[:max_articles_per_seed]:
                self.urls.append(self._extract_url(element))
                if len(self.urls) == max_articles:
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

    is_crawler_config_ok = True
    if not isinstance(crawler_config, dict):
        is_crawler_config_ok = False
        raise UnknownConfigError

    if not isinstance(crawler_config['base_urls'], list) or \
            not all(isinstance(url, str) for url in crawler_config['base_urls']):
        is_crawler_config_ok = False
        raise IncorrectURLError

    if not isinstance(crawler_config['total_articles_to_find_and_parse'], int):
        is_crawler_config_ok = False
        raise IncorrectNumberOfArticlesError

    if crawler_config['total_articles_to_find_and_parse'] >= 1000000:
        is_crawler_config_ok = False
        raise NumberOfArticlesOutOfRangeError

    if is_crawler_config_ok:
        return crawler_config.values()


if __name__ == '__main__':
    # YOUR CODE HERE
    import constants

    seed_urls, max_articles, max_articles_per_seed = validate_config(constants.CRAWLER_CONFIG_PATH)
    crawler = Crawler(seed_urls, max_articles, max_articles_per_seed)
    print(crawler.find_articles())
