"""
Crawler implementation
"""
import os
import json
import time

from json.decoder import JSONDecodeError
from collections import namedtuple
from datetime import datetime
from random import randint
from typing import Set, List

import requests
from bs4 import BeautifulSoup
import shutil
from pathlib import Path

from constants import CRAWLER_CONFIG_PATH, HEADERS, COOKIES, ASSETS_PATH
from article import Article


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
    seed_urls: List[str]
    max_articles: int
    max_articles_per_seed: int
    urls: Set[str]

    def __init__(self, seed_urls: list, max_articles: int, max_articles_per_seed: int):
        self.seed_urls = seed_urls
        self.max_articles = max_articles
        self.max_articles_per_seed = max_articles_per_seed
        self.urls = set()

    @staticmethod
    def _extract_url(article_bs: BeautifulSoup):
        """
        Extracts news urls from the seed page
        """
        news = article_bs.select('div.col-md-9 div.col-md-6 h2 a')
        links = [article.attrs['href'] for article in news]

        return links

    def find_articles(self):
        """
        Finds articles
        """
        with requests.Session() as session:
            session.headers.update({**HEADERS, **COOKIES})

            for url in self.get_search_urls():
                num_articles = min(self.max_articles_per_seed, self.max_articles)

                response = session.get(url)

                if not response:
                    raise IncorrectURLError

                soup = BeautifulSoup(response.text, 'lxml')
                links = Crawler._extract_url(soup)[:num_articles]

                self.urls.add(*links)

                self.get_search_urls()
                time.sleep(randint(3, 5))

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        yield from self.seed_urls


class CrawlerRecursive(Crawler):
    """
    Recursive Crawler
    """
    def get_search_urls(self):
        response = requests.get(self.seed_urls[0], headers=HEADERS, cookies=COOKIES)

        soup = BeautifulSoup(response.text, 'lxml')
        next_page = soup.select_one('ul.pagination li:nth-child(2) a')

        if next_page:
            yield next_page['href']

        self.seed_urls[0] = response.url


class ArticleParser:
    """
    ArticleParser implementation
    """
    article: Article
    full_url: str
    article_id: int

    def __init__(self, full_url: str, article_id: int) -> None:
        self.full_url = full_url
        self.article_id = article_id
        self.article = Article(full_url, article_id)

    def _fill_article_with_text(self, article_soup):
        soup = BeautifulSoup(article_soup, 'lxml')

        self.article.text = '\n'.join([p.text for p in soup.select('.entry-content p.a')])

    def _fill_article_with_meta_information(self, article_soup):
        soup = BeautifulSoup(article_soup, 'lxml')

        self.article.title = soup.select_one('h1').text
        self.article.author = soup.select_one('li.autor').text

        date: str = soup.select_one('time.entry-date').attrs['datetime']
        self.article.date = self.unify_date_format(date)

        self.article.topics = [tag.text for tag in soup.select('a[rel^="category"]')]

        views: str = soup.select_one('.entry-meta li:nth-last-child(2)').text.strip()
        self.article.views = int(views)

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
        response = requests.get(self.full_url, headers=HEADERS, cookies=COOKIES)

        if not response:
            raise IncorrectURLError

        soup = BeautifulSoup(response.text, features='lxml')

        self._fill_article_with_text(soup)
        self._fill_article_with_meta_information(soup)

        self.article.save_raw()


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    shutil.rmtree(base_path, ignore_errors=True)
    Path(base_path).mkdir(parents=True, exist_ok=True)

    # if not os.path.exists(base_path):
    #     os.makedirs(base_path)

    # if not os.path.exists(os.path.join(PROJECT_ROOT, 'tmp', 'pages')):
    #     os.makedirs(os.path.join(PROJECT_ROOT, 'tmp', 'pages'))
    #
    # if not os.path.exists(os.path.join(base_path, 'tmp', 'articles')):
    #     os.makedirs(os.path.join(base_path, 'tmp', 'articles'))


def validate_config(crawler_path: str):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        config: dict = json.load(file)

    Check = namedtuple('Check', ['status', 'error'])

    try:
        is_correct_type_total_num = isinstance(config['total_articles_to_find_and_parse'], int)
        is_correct_url = all(isinstance(x, str) for x in config['base_urls'])
        is_num_not_oor = is_correct_type_total_num and 0 < config['total_articles_to_find_and_parse'] <= 5000

        checks = (
            Check(is_correct_url, IncorrectURLError),
            Check(is_correct_type_total_num, IncorrectNumberOfArticlesError),
            Check(is_num_not_oor, NumberOfArticlesOutOfRangeError)
        )

        for check in checks:
            if not check.status:
                raise check.error

        return config.values()

    except (JSONDecodeError, KeyError) as error:
        raise UnknownConfigError from error


if __name__ == '__main__':
    urls, max_num_articles, max_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    crawler = CrawlerRecursive(seed_urls=urls, max_articles=max_num_articles, max_articles_per_seed=max_per_seed)

    crawler.find_articles()

    prepare_environment(ASSETS_PATH)

    for idx, article_url in enumerate(crawler.urls):
        parser = ArticleParser(full_url=article_url, article_id=idx)
        parser.parse()
