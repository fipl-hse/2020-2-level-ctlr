"""
Crawler implementation
"""
from datetime import datetime
import json
import os
import shutil

from bs4 import BeautifulSoup
import requests

from article import Article
from constants import CRAWLER_CONFIG_PATH, ASSETS_PATH


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
        url_article = article_bs.find('h2', class_="entry-title").find('a')
        return url_article.attrs['href']

    def find_articles(self):
        """
        Finds articles
        """
        self.get_search_urls()
        for url in self.seed_urls:
            response = requests.get(url, headers=HEADERS)
            if not response:
                raise IncorrectURLError
            page_soup = BeautifulSoup(response.content, features='lxml')
            main_soup = page_soup.find('main', id='main')
            articles_soup = main_soup.find_all('article')
            for i in range(self.max_articles_per_seed):
                if len(self.urls) < self.max_articles and i < len(articles_soup):
                    self.urls.append(self._extract_url(articles_soup[i]))
                else:
                    break
            if len(self.urls) == self.max_articles:
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
        self.full_url = full_url
        self.article_id = article_id
        self.article = Article(full_url, article_id)

    def _fill_article_with_text(self, article_soup):
        article_texts = article_soup.find_all('p')
        collected_text = []
        for par in article_texts:
            if 'class' not in par.attrs:
                collected_text.append(par.text.strip())
        self.article.text = ' '.join(collected_text)

    def _fill_article_with_meta_information(self, article_soup):
        # find title
        self.article.title = article_soup.find('h1', class_="entry-title").text

        # find topics
        for topic in article_soup.find_all('a', rel="category tag"):
            self.article.topics.append(topic.text)

        # find author
        self.article.author = article_soup.find('span', class_="author vcard").find('a').text

        # find date
        date_art = self.unify_date_format(article_soup.find('time', class_="entry-date published").text)
        self.article.date = date_art

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format: "%Y-%m-%d %H:%M:%S"
        """
        return datetime.strptime(date_str, "%d.%m.%Y")

    def parse(self):
        """
        Parses each article
        """
        response = requests.get(self.full_url, headers=HEADERS)
        if not response:
            raise IncorrectURLError

        article_soup = BeautifulSoup(response.content, features='lxml')
        self._fill_article_with_text(article_soup)
        self._fill_article_with_meta_information(article_soup)


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    shutil.rmtree(base_path, ignore_errors=True)
    try:
        os.makedirs(base_path, mode=0o777)
    except OSError as error:
        raise UnknownConfigError from error


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as file:
        crawler = json.load(file)
    url_pattern = 'http://kmvexpress.ru/'

    for url in crawler['base_urls']:
        if not isinstance(url, str) or url_pattern not in url:
            raise IncorrectURLError

    try:
        max_articles = crawler['total_articles_to_find_and_parse']
        if not isinstance(max_articles, int):
            raise IncorrectNumberOfArticlesError
        if max_articles > 100:
            raise NumberOfArticlesOutOfRangeError

    except KeyError as error:
        raise UnknownConfigError from error

    try:
        max_articles_per_seed = crawler['max_number_articles_to_get_from_one_seed']
        if not isinstance(max_articles_per_seed, int):
            raise IncorrectNumberOfArticlesError

    except KeyError as error:
        raise UnknownConfigError from error

    seed_urls = crawler['base_urls']
    return seed_urls, max_articles, max_articles_per_seed


def get_headers_config(crawler_path):
    """
    Gets HEADERS param from config file
    """
    with open(crawler_path, 'r', encoding='utf-8') as file:
        crawler = json.load(file)

    headers_config = crawler['headers']
    if not isinstance(headers_config, dict):
        raise UnknownConfigError

    return headers_config


if __name__ == '__main__':
    # YOUR CODE HERE
    urls, max_num_articles, max_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    HEADERS = get_headers_config(CRAWLER_CONFIG_PATH)
    crawler_current = Crawler(seed_urls=urls, max_articles=max_num_articles, max_articles_per_seed=max_per_seed)
    crawler_current.find_articles()

    prepare_environment(ASSETS_PATH)
    for ind, article_url in enumerate(crawler_current.urls):
        parser = ArticleParser(full_url=article_url, article_id=ind+1)
        parser.parse()
        parser.article.save_raw()
