"""
Crawler implementation
"""

import requests
import json
from bs4 import BeautifulSoup
from time import sleep
import random
from article import Article
import os


headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'
           'Chrome/88.0.4324.152 YaBrowser/21.2.2.102 Yowser/2.5 Safari/537.36'}


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
        url = article_bs.content[1]
        return url.get('href')

    def find_articles(self):
        """
        Finds articles
        """
        self.get_search_urls()
        for url in self.seed_urls:
            response = requests.get(str(url))
            if not response:
                raise IncorrectURLError
            if len(self.urls) < self.max_articles:
                self.urls.append(url)
            else:
                break

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
        text_soup = article_soup.find_all('p')
        text = ''
        for element in text_soup[:4]:
            text += element.text
        return text.strip()

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find('h1').text.strip()
        return None

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
        response = requests.get(self.full_url, headers=headers)
        if not response:
            raise IncorrectURLError
        article_soup = BeautifulSoup(response.content, features='lxml')
        self.article.text += self._fill_article_with_text(article_soup)
        self._fill_article_with_meta_information(article_soup)
        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if not os.path.isdir(base_path):
        os.makedirs(base_path)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r') as crawler_config_file:
        config = json.load(crawler_config_file)

    if not isinstance(config, dict):
        raise UnknownConfigError

    if 'base_urls' not in config or not isinstance(config['base_urls'], list) or \
            not all([isinstance(url, str) for url in config['base_urls']]):
        raise IncorrectURLError

    if 'total_articles_to_find_and_parse' in config and \
        isinstance(config['total_articles_to_find_and_parse'], int) and \
            config['total_articles_to_find_and_parse'] > 100:
        raise NumberOfArticlesOutOfRangeError

    if 'max_number_articles_to_get_from_one_seed' not in config or \
        not isinstance(config['max_number_articles_to_get_from_one_seed'], int) or \
            not isinstance(config['total_articles_to_find_and_parse'], int):
        raise IncorrectNumberOfArticlesError

    urls_list = config['base_urls']
    total_art = config['total_articles_to_find_and_parse']
    max_number = config['max_number_articles_to_get_from_one_seed']
    return urls_list, total_art, max_number


if __name__ == '__main__':
    # YOUR CODE HERE
    from constants import CRAWLER_CONFIG_PATH
    from constants import ASSETS_PATH

    urls_list, total_art, max_number = validate_config(CRAWLER_CONFIG_PATH)
    crawler = Crawler(seed_urls=urls_list, max_articles=total_art, max_articles_per_seed=max_number)
    urls = crawler.find_articles()
    prepare_environment(ASSETS_PATH)
    article_id = 0
    for article_url in urls:
        article_id += 1
        parser = ArticleParser(article_url, article_id)
        sleep(random.randint(2, 4))
        article = parser.parse()
        article.save_raw()
