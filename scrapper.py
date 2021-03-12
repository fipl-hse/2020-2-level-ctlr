"""
Crawler implementation
"""

import os
import json
import shutil
from datetime import datetime
from random import randrange
from time import sleep
import requests
from bs4 import BeautifulSoup
from requests import HTTPError
import article
from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH

HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/88.0.4324.190 Safari/537.36 '
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
        return article_bs.find('a').get('href')

    def find_articles(self):
        """
        Finds articles
        """
        try:
            for seed_url in self.seed_urls:
                response = requests.get(seed_url, headers=HEADERS)
                response.raise_for_status()

                seed_soup = BeautifulSoup(response.content, 'lxml')
                articles = seed_soup.find_all('h2', class_='entry-title')

                for article_number in range(self.max_articles_per_seed):
                    article_soup = articles[article_number]
                    self.urls.append(self._extract_url(article_soup))

                    if len(self.urls) == self.max_articles:
                        break

                if len(self.urls) == self.max_articles:
                    break
        except HTTPError as error:
            print(error)

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
        self.article = article.Article(url=full_url, article_id=str(article_id))

    def _fill_article_with_text(self, article_soup):
        self.article.text = article_soup.find('div', class_='entry entry-content').text.strip()

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find('h1', class_='entry-title').text.strip()

        self.article.date = self.unify_date_format(article_soup.find('span', class_="meta-date").text.strip())

        self.article.author = article_soup.find('span', class_="meta-author").find('a').text.strip()

        topics = article_soup.find('span', class_="meta-cat").find_all('a')
        for topic in topics:
            self.article.topics.append(topic.text.strip())

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format
        """
        date_list = [int(num) for num in date_str.split('.')]
        date_datetime = datetime(date_list[2], date_list[1], date_list[0], 0, 0, 0)

        return date_datetime

    def parse(self):
        """
        Parses each article
        """
        try:
            response = requests.get(self.full_url, headers=HEADERS)
            response.raise_for_status()
        except HTTPError as error:
            print(error)
        else:
            article_bs = BeautifulSoup(response.content, 'lxml')

            self._fill_article_with_text(article_bs)
            self._fill_article_with_meta_information(article_bs)

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
    with open(crawler_path, 'r', encoding='utf-8') as file:
        crawler_config = json.load(file)

    if (not isinstance(crawler_config['base_urls'], list) or
            not all([isinstance(seed_url, str) for seed_url in crawler_config['base_urls']])):
        raise IncorrectURLError

    if ('total_articles_to_find_and_parse' in crawler_config and
            isinstance(crawler_config['total_articles_to_find_and_parse'], int) and
            crawler_config['total_articles_to_find_and_parse'] > 100):
        raise NumberOfArticlesOutOfRangeError

    if (not isinstance(crawler_config['total_articles_to_find_and_parse'], int) or
            isinstance(crawler_config['total_articles_to_find_and_parse'], bool)):
        raise IncorrectNumberOfArticlesError

    return (crawler_config['base_urls'],
            crawler_config['total_articles_to_find_and_parse'],
            crawler_config['max_number_articles_to_get_from_one_seed'])


if __name__ == '__main__':
    # YOUR CODE HERE
    prepare_environment(ASSETS_PATH)

    seed_urls_list, max_num_articles, max_num_per_seed = validate_config(CRAWLER_CONFIG_PATH)

    crawler = Crawler(seed_urls=seed_urls_list,
                      max_articles=max_num_articles,
                      max_articles_per_seed=max_num_per_seed)
    crawler.find_articles()

    for article_id_number, article_url in enumerate(crawler.urls, 1):
        parser = ArticleParser(full_url=article_url, article_id=article_id_number)
        article_parsed = parser.parse()
        article_parsed.save_raw()
        sleep(randrange(3, 5))
