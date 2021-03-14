"""
Crawler implementation
"""
import re
import os
import json
import shutil
from datetime import datetime
from random import randint
from time import sleep
import requests
from bs4 import BeautifulSoup
from article import Article

from constants import CRAWLER_CONFIG_PATH
from constants import ASSETS_PATH

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/88.0.4324.190 Safari/537.36'}


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
        self.max_articles_per_speed = max_articles_per_seed
        self.urls = []

    @staticmethod
    def _extract_url(article_bs):
        return article_bs.find("a").get("href")

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            response = requests.get(seed_url, headers=HEADERS)
            sleep(randint(3, 7))
            response.encoding = 'utf-8'
            page_soup = BeautifulSoup(response.content, features='lxml')
            articles = page_soup.find_all('h3', class_='entry-title')
            for article in articles:
                if len(self.urls) <= self.max_articles and article not in self.urls:
                    seed_url = self._extract_url(article)
                    self.urls.append(seed_url)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.urls


class ArticleParser:
    """
    ArticleParser implementation
    """

    def __init__(self, full_url: str, article_id: int):
        self.full_url = full_url
        self.article_id = article_id
        self.article = Article(full_url, article_id)

    def _fill_article_with_text(self, article_soup):
        article_text_list = []
        text_soup = article_soup.find('div', class_='entry-content').text[:-18]
        article_text_list.append(text_soup)
        self.article.text = '\n'.join(article_text_list)

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find('h1', class_='block-title wow zoomIn').text.strip()

        date_soup = article_soup.find('div', class_='entry-meta')
        date = re.findall(r'\d.{9}', str(date_soup))
        ok_date = ''.join(date)
        self.article.date = self.unify_date_format(ok_date)

        self.article.author = 'NOT FOUND'

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format
        """
        return datetime.strptime(date_str, "%d.%m.%Y")

    def parse(self):
        """
        Parses each article
        """
        response = requests.get(self.full_url, headers=HEADERS)
        if response:
            article_soup = BeautifulSoup(response.content, features='lxml')
            self._fill_article_with_text(article_soup)
            self._fill_article_with_meta_information(article_soup)
        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if os.path.exists(base_path):
        shutil.rmtree(base_path)
    os.makedirs(base_path)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        crawler_config = json.load(file)

    if ('base_urls' not in crawler_config
            or not isinstance(crawler_config['base_urls'], list)
            or not all([isinstance(url, str) for url in crawler_config['base_urls']])):
        raise IncorrectURLError

    if ('total_articles_to_find_and_parse' in crawler_config and
            isinstance(crawler_config['total_articles_to_find_and_parse'], int)
            and crawler_config['total_articles_to_find_and_parse'] > 101):
        raise NumberOfArticlesOutOfRangeError

    if (not isinstance(crawler_config['total_articles_to_find_and_parse'], int)
            or 'total_articles_to_find_and_parse' not in crawler_config
            or 'max_number_articles_to_get_from_one_seed' not in crawler_config):
        raise IncorrectNumberOfArticlesError

    return (crawler_config['base_urls'],
            crawler_config['total_articles_to_find_and_parse'],
            crawler_config['max_number_articles_to_get_from_one_seed'])


if __name__ == '__main__':
    prepare_environment(ASSETS_PATH)

    urls_list, max_articles_num, max_articles_num_per_seed = validate_config(CRAWLER_CONFIG_PATH)

    crawler = Crawler(seed_urls=urls_list,
                      max_articles=max_articles_num,
                      max_articles_per_seed=max_articles_num)
    crawler.find_articles()

    for article_id_n, article_url in enumerate(crawler.urls, 1):
        parser = ArticleParser(full_url=article_url, article_id=article_id_n)
        parsed_article = parser.parse()
        parsed_article.save_raw()
