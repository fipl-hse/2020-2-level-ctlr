"""
Crawler implementation
"""
import json
import random
import os
import shutil
import re
from time import sleep

from datetime import datetime
import requests
from bs4 import BeautifulSoup

from article import Article
from constants import ASSETS_PATH
from constants import CRAWLER_CONFIG_PATH
from constants import HEADERS


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
        raw_urls_list = []
        link_sample = re.compile(r'/\d{6}.+')
        for link_container in article_bs.find_all(name='a'):
            link_itself = link_container.get('href')
            if re.match(link_sample, str(link_itself)) and str(link_itself) not in raw_urls_list:
                raw_urls_list.append(link_itself)
        return raw_urls_list

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            if len(self.urls) < self.total_max_articles:
                response = requests.get(seed_url, headers=HEADERS)
                print('Making a request...')
                sleep_interval = random.randrange(2, 5)
                sleep(sleep_interval)
                article_bs = BeautifulSoup(response.content, features='lxml')
                raw_urls_list = self._extract_url(article_bs)[:self.max_articles_per_seed]
                for link in raw_urls_list:
                    if len(self.urls) < self.total_max_articles:
                        self.urls.append('https://www.infpol.ru' + link)
                    else:
                        break
            else:
                break

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
        self.article_url = full_url
        self.i = article_id
        self.article = Article(full_url, article_id)

    def _fill_article_with_text(self, article_soup):
        self.article.text = '\n'.join(abstract.text for abstract in article_soup.find_all(name='p'))

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find(name='h1').text
        self.article.date = self.unify_date_format(article_soup.find(name='time', class_='js-time').get('datetime'))
        self.article.author = article_soup.find(class_='author').text.split(': ')[1]
        topics = article_soup.find(name='div', class_='tags').text
        self.article.topics = [topic for topic in topics.split('\n') if topic]

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format
        """
        return datetime.fromisoformat(date_str)

    def parse(self):
        """
        Parses each article
        """
        response = requests.get(self.article_url, headers=HEADERS)
        print('The webpage is being requested...')
        if not response:
            raise IncorrectURLError
        print('Request is OK')
        article_bs = BeautifulSoup(response.content, features='lxml')
        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if os.path.exists(base_path):
        shutil.rmtree(os.path.dirname(base_path))
    os.makedirs(base_path)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r') as crawler:
        data = json.load(crawler)

    validating_seed_urls = data.get("base_urls")
    validating_max_articles = data.get("total_articles_to_find_and_parse")
    validating_max_articles_per_seed = data.get("max_number_articles_to_get_from_one_seed")

    if not isinstance(data, dict) or not data:
        raise UnknownConfigError

    for base_url in validating_seed_urls:
        if not re.match(r'https://www\.[\d\w-]+\..+', base_url):
            raise IncorrectURLError

    if not isinstance(validating_max_articles, int):
        raise IncorrectNumberOfArticlesError

    if validating_max_articles >= 1000:
        raise NumberOfArticlesOutOfRangeError

    return validating_seed_urls, validating_max_articles, validating_max_articles_per_seed


if __name__ == '__main__':
    proper_seed_urls, proper_max_articles, proper_max_articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    example = Crawler(proper_seed_urls, proper_max_articles, proper_max_articles_per_seed)
    example.find_articles()
    prepare_environment(ASSETS_PATH)
    for index, url in enumerate(example.urls, 1):
        parser = ArticleParser(url, index)
        article = parser.parse()
        article.save_raw()
        sleep(random.randrange(2, 5))
