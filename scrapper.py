"""
Crawler implementation
"""

import datetime
import json
import os
from random import randint
import shutil
from time import sleep

from bs4 import BeautifulSoup
import requests

import article
from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH

HEADERS = {
    'user-agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'}


class UnknownConfigError(Exception):
    """
    Most general error
    """


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


class IncorrectStatusCode(Exception):
    """"
    Custom error
    """


class Crawler:
    """
    Crawler implementation
    """

    def __init__(self, seed_urls: list, max_articles: int, max_articles_per_seed: int):
        self.seed_urls = seed_urls
        self.max_articles_per_seed = max_articles_per_seed
        self.max_articles = max_articles
        self.urls = []

    @staticmethod
    def _extract_url(article_bs):
        pages_links = []
        for tag_a_content in article_bs.find_all('div', class_='signature'):
            link = tag_a_content.find('a').get('href')
            if link and link not in pages_links:
                pages_links.append('http://ks-yanao.ru' + link)
        return pages_links

    def find_articles(self):
        """
        Finds articles
        """
        seed_urls = self.get_search_urls()
        for seed_url in seed_urls:
            try:
                response = requests.get(seed_url, headers=HEADERS)
                sleep(randint(2, 6))
                if response.status_code:
                    main_page_soup = BeautifulSoup(response.content, features='lxml')
                else:
                    raise IncorrectStatusCode
            except IncorrectStatusCode:
                continue
            else:
                found_links = self._extract_url(main_page_soup)
                if len(found_links) < self.max_articles_per_seed:
                    self.urls.extend(found_links)
                else:
                    self.urls.extend(found_links[:self.max_articles_per_seed])

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
        self.article = article.Article(full_url, article_id)

    def _fill_article_with_text(self, article_soup):
        paragraphs_soup = article_soup.find('div', class_='element-detail')
        article_list = [paragraph.strip() for paragraph in paragraphs_soup.text.split('\n') if paragraph.strip()]
        article_str = ' '.join(article_list)
        self.article.text = article_str

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find('h1').text.strip()

        try:
            self.article.author = article_soup.find('a', class_='author-name font-open-s').text.strip()
        except AttributeError:
            self.article.author = 'NOT FOUND'

        date_from_url = article_soup.find('p', class_='date font-open-s-light').text
        self.article.date = self.unify_date_format(date_from_url)

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format
        """
        return datetime.datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S")

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
    with open(crawler_path) as opened_file:
        config = json.load(opened_file)

    is_config_unknown = ('base_urls' not in config
                         or 'total_articles_to_find_and_parse' not in config
                         or 'max_number_articles_to_get_from_one_seed' not in config)
    if not isinstance(config, dict) and is_config_unknown:
        raise UnknownConfigError

    are_urls_incorrect = (not isinstance(config['base_urls'], list)
                          or not all([isinstance(url, str) for url in config['base_urls']])
                          or len([url for url in config['base_urls'] if 'http://ks-yanao.ru/' in url])
                          != len(config['base_urls']))
    if are_urls_incorrect:
        raise IncorrectURLError

    is_num_articles_incorrect = (not isinstance(config['total_articles_to_find_and_parse'], int)
                                 or config['total_articles_to_find_and_parse'] < 0)
    if is_num_articles_incorrect:
        raise IncorrectNumberOfArticlesError

    is_num_out_of_range = (config['total_articles_to_find_and_parse'] > 100)
    if is_num_out_of_range:
        raise NumberOfArticlesOutOfRangeError

    return config['base_urls'], \
           config['total_articles_to_find_and_parse'], \
           config['max_number_articles_to_get_from_one_seed']


if __name__ == '__main__':
    # YOUR CODE HERE
    prepare_environment(ASSETS_PATH)
    seed_urls_ex, max_articles_ex, max_articles_per_seed_ex = validate_config(CRAWLER_CONFIG_PATH)
    crawler = Crawler(seed_urls=seed_urls_ex,
                      max_articles=max_articles_ex,
                      max_articles_per_seed=max_articles_per_seed_ex)
    crawler.find_articles()
    for art_id, art_url in enumerate(crawler.urls, 1):
        parser = ArticleParser(full_url=art_url, article_id=art_id)
        article_from_list = parser.parse()
        article_from_list.save_raw()
        sleep(randint(3, 5))
