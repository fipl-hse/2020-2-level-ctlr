"""
Crawler implementation
"""
from time import sleep

import json
import requests
import re
from bs4 import BeautifulSoup

from constants import CRAWLER_CONFIG_PATH

headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Mobile Safari/537.36'
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
    def __init__(self, seed_urls: list, max_article: int, max_articles_per_seed: int):
        self.seed_urls = seed_urls
        self.max_article = max_article
        self.max_articles_per_seed = max_articles_per_seed
        self.urls = []

    @staticmethod
    def _extract_url(article_bs):
        pass

    def find_articles(self):
        """
        Finds articles
        """
        urls = []
        main_link = "http://www.kprfast.ru"
        for url in self.seed_urls:
            response = requests.get(url, headers=headers)
            sleep(5)
            print('made request')
            page_soup = BeautifulSoup(response.content, features='lxml')
            all_links = page_soup.find_all(class_="readmore")
            for element in all_links:
                link_href = element.find("a").get("href")
                urls.append(link_href)
            for link in urls:
                self.urls.append(main_link + link)
        return []

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
    with open(crawler_path, "r") as crawler:
        check_config = json.load(crawler)
    validate_seed_urls = check_config.get("base_urls")
    validate_max_article = check_config.get("total_articles_to_find_and_parse")
    validate_max_articles_per_seed = check_config.get("max_number_articles_to_get_from_one_seed")

    if not isinstance(validate_seed_urls, list) or not isinstance(validate_max_article, int)\
            or not isinstance(validate_max_articles_per_seed, int):
        raise UnknownConfigError

    for each_link in validate_seed_urls:
        result = re.match(r'http://www', each_link)
        if result == 'None':
            raise IncorrectURLError

    if validate_max_article == 0:
        raise NumberOfArticlesOutOfRangeError

    if validate_max_articles_per_seed == 0:
        raise IncorrectNumberOfArticlesError

    return validate_seed_urls, validate_max_article, validate_max_articles_per_seed


if __name__ == '__main__':
    # YOUR CODE HERE
    seed_urls, max_articles, max_articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    check_1 = Crawler(seed_urls, max_articles, max_articles_per_seed)
    check_1.find_articles()



