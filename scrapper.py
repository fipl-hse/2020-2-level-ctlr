"""
Crawler implementation
"""
import json
import os
import time
import random
import shutil
import logging.config

from json.decoder import JSONDecodeError
from collections import namedtuple
from datetime import datetime
from typing import Set, List, Iterable, Iterator, Union, Dict, Tuple
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from requests import RequestException

from constants import CRAWLER_CONFIG_PATH, HEADERS, COOKIES, ASSETS_PATH, CRAWLER_INTERIM
from article import Article

logging.config.fileConfig(fname='crawler_logging.ini', disable_existing_loggers=False)
log = logging.getLogger(__name__)


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
    def _extract_url(article_bs: BeautifulSoup) -> List[str]:
        """
        Extracts news urls from the seed page
        """
        news = article_bs.select('div.col-md-9 div.col-md-6 h2 a')
        links = [article.attrs['href'] for article in news]

        return links

    @staticmethod
    def save_interim(**args) -> None:
        interim: dict = {**args}

        with open(CRAWLER_INTERIM, "w", encoding='utf-8') as file:
            json.dump(interim,
                      file,
                      sort_keys=False,
                      indent=4,
                      ensure_ascii=False,
                      separators=(',', ': '))

    @staticmethod
    def load_interim() -> Tuple[list, set, list]:
        with open(CRAWLER_INTERIM, encoding='utf-8') as file:
            status: dict = json.load(file)

        return status['seed'], set(status['articles']), status.get('processed')

    def find_articles(self) -> None:
        """
        Finds articles
        """
        with requests.Session() as session:
            for url in self.get_search_urls():

                try:
                    response = session.get(url, headers=HEADERS, cookies=COOKIES)
                    response.raise_for_status()
                except RequestException as exc:
                    log.exception("%s was encountered while getting seed_urls", exc)
                    return

                soup = BeautifulSoup(response.text, 'lxml')

                seed_articles = self._extract_url(soup)[:self.max_articles_per_seed]
                links = seed_articles[:self.max_articles - len(self.urls)]

                self.urls.update(links)
                self.save_interim(seed=url, articles=list(self.urls))

                log.info("Seed page '%s' is processed.", url)

                time.sleep(random.uniform(2, 4))

                if len(self.urls) == self.max_articles:
                    self.save_interim(seed=url, articles=list(self.urls), processed=[])
                    break

    def get_search_urls(self) -> Iterator[str]:
        """
        Returns seed_urls param
        """
        yield self.seed_urls


class CrawlerRecursive(Crawler):
    """
    Recursive Crawler
    """
    def get_search_urls(self) -> Iterator[str]:
        if os.path.exists(CRAWLER_INTERIM):
            self.seed_urls[0], self.urls, processed = self.load_interim()

            if processed is not None:
                log.info('All seed_urls are processed.')
                return

        try:

            while True:
                response = requests.get(self.seed_urls[0], headers=HEADERS, cookies=COOKIES)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'lxml')
                next_page = soup.select_one('ul.pagination li:has(span.current) + li a')

                self.seed_urls.append(next_page['href'])
                yield self.seed_urls.pop(0)

        except RequestException as exc:
            log.exception("%s was encountered while getting seed_urls", exc)
            return


class ArticleParser:
    """
    ArticleParser implementation
    """
    article: Article
    full_url: str
    article_id: int

    def __init__(self, full_url: str, article_id: int):
        self.full_url = full_url
        self.article_id = article_id
        self.article = Article(full_url, article_id)

    def _fill_article_with_text(self, article_soup: BeautifulSoup) -> None:
        self.article.text = '\n'.join([p.text for p in article_soup.select('.entry-content > p')])

    def _fill_article_with_meta_information(self, article_soup: BeautifulSoup) -> None:
        self.article.title = article_soup.select_one('h1').text
        self.article.author = article_soup.select_one('li.autor').text

        date: str = article_soup.select_one('time.entry-date').attrs['datetime']
        self.article.date = self.unify_date_format(date)

        self.article.topics = [tag.text for tag in article_soup.select('a[rel^="category"]')]

    @staticmethod
    def unify_date_format(date_str: str) -> datetime:
        """
        Unifies date format
        """
        return datetime.fromisoformat(date_str)

    def parse(self) -> None:
        """
        Parses each article
        """
        try:
            response = requests.get(self.full_url, headers=HEADERS, cookies=COOKIES)
            response.raise_for_status()
        except RequestException as exc:
            log.exception("%s was encountered while parsing the article", exc)
            return

        soup = BeautifulSoup(response.text, features='lxml')

        self._fill_article_with_text(soup)
        self._fill_article_with_meta_information(soup)

        self.article.save_raw()


def prepare_environment(base_path: str) -> None:
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    shutil.rmtree(base_path, ignore_errors=True)
    Path(base_path).mkdir(parents=True, exist_ok=True)


def validate_config(crawler_path: str) -> Iterable:
    """
    Validates given config
    """
    with open(crawler_path) as file:
        config: Dict[str, Union[str, int]] = json.load(file)

    Check = namedtuple('Check', ['status', 'error'])

    try:
        total_num = config['total_articles_to_find_and_parse']

        is_correct_total_num = isinstance(total_num, int)
        is_correct_url = all(isinstance(x, str) for x in config['base_urls'])
        is_num_not_oor = is_correct_total_num and 0 < total_num <= 100000

        checks = (
            Check(is_correct_url, IncorrectURLError),
            Check(is_correct_total_num, IncorrectNumberOfArticlesError),
            Check(is_num_not_oor, NumberOfArticlesOutOfRangeError),
        )

        for check in checks:
            if not check.status:
                raise check.error

        return config.values()

    except (JSONDecodeError, KeyError) as exc:
        log.exception("%s was encountered while validating crawler config.", exc)
        raise UnknownConfigError from exc


if __name__ == '__main__':
    urls, max_num_articles, max_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    crawler = CrawlerRecursive(seed_urls=urls, max_articles=max_num_articles, max_articles_per_seed=max_per_seed)

    if not os.path.exists(ASSETS_PATH):
        prepare_environment(ASSETS_PATH)

    crawler.find_articles()
    seed, articles, parsed = crawler.load_interim()

    for idx, article_url in enumerate(sorted(crawler.urls)):
        parser = ArticleParser(full_url=article_url, article_id=idx)
        time.sleep(random.uniform(2, 4))

        if article_url in parsed:
            log.info("Article #%s '%s' is already processed. Skipping.", idx, article_url)
            continue

        parser.parse()
        parsed.append(article_url)

        crawler.save_interim(seed=seed, articles=list(articles), processed=parsed)
        log.info("Article #%s '%s' is processed.", idx, article_url)

    log.info("Total: %s articles.", len(crawler.urls))
