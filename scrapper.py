"""
Crawler implementation
"""
import datetime
import json
import os
import random
import re
import shutil
from time import sleep


from bs4 import BeautifulSoup
import requests

from article import Article
from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/88.0.4324.41 YaBrowser/21.2.0.1097 Yowser/2.5 Safari/537.36'}


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
        page_urls = list(map(lambda x: x.find('a').attrs['href'],
                             article_bs.find_all('div', {'class': 'news-preview-content'})))
        return ['https://vn.ru' + page_url for page_url in page_urls[:max_articles_num_per_seed]]

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.get_search_urls():
            try:
                response = requests.get(seed_url, headers=headers)
                sleep(random.randint(2, 6))
                response.encoding = 'utf-8'
                if not response:
                    raise IncorrectURLError

            except IncorrectURLError:
                continue

            page_bs = BeautifulSoup(response.content, features='lxml')
            urls_list = self._extract_url(article_bs=page_bs)

            urls_number = min(max_articles_num_per_seed, (max_articles_num - len(self.urls)))
            self.urls.extend(urls_list[:urls_number])

            if len(self.urls) == max_articles_num:
                return self.urls

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

    @staticmethod
    def clean_text(text):
        return '\n'.join(re.findall(r'[А-я]+.+\.[ \t]*', text, flags=re.MULTILINE))

    def _fill_article_with_text(self, article_soup):
        article_preview = article_soup.find('div', {'class': 'one-news-preview-text'}).text + '\n'

        article_content = article_soup.find('div', {'class': 'js-mediator-article'}).text
        self.article.text = article_preview + self.clean_text(article_content)

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find('h1').text

        self.article.author = article_soup.find('div', {'class': 'author-name'}).text.strip('\n')

        raw_topics = article_soup.find_all('div', {'class': 'on-footer-row'})[1]
        self.article.topics = [raw_topics.text.lower()]

        raw_date = article_soup.find('div', {'class': 'nw-dn-date'}).text
        self.article.date = self.unify_date_format(raw_date)

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format
        """

        return datetime.datetime.strptime(date_str, '%d.%m.%Y')

    def parse(self):
        """
        Parses each article
        """

        response = requests.get(self.full_url, headers=headers)

        if not response:
            raise IncorrectURLError

        article_bs = BeautifulSoup(response.content, features='lxml')

        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)


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
        config = json.load(file)

    if 'base_urls' not in config or not isinstance(config['base_urls'], list):
        raise IncorrectURLError

    for url in config['base_urls']:
        if not isinstance(url, str) or not url.startswith('https://'):
            raise IncorrectURLError

    if 'total_articles_to_find_and_parse' in config and \
            isinstance(config['total_articles_to_find_and_parse'], int) and \
            config['total_articles_to_find_and_parse'] not in range(0, 101):
        raise NumberOfArticlesOutOfRangeError

    if 'total_articles_to_find_and_parse' not in config or \
            not isinstance(config['total_articles_to_find_and_parse'], int) or \
            'max_number_articles_to_get_from_one_seed' not in config or \
            not isinstance(config['max_number_articles_to_get_from_one_seed'], int):
        raise IncorrectNumberOfArticlesError

    return config['base_urls'], \
           config['total_articles_to_find_and_parse'], \
           config['max_number_articles_to_get_from_one_seed']


if __name__ == '__main__':
    urls, max_articles_num, max_articles_num_per_seed = validate_config(CRAWLER_CONFIG_PATH)

    crawler = Crawler(seed_urls=urls,
                      max_articles=max_articles_num,
                      max_articles_per_seed=max_articles_num_per_seed)
    links = crawler.find_articles()

    prepare_environment(ASSETS_PATH)
    for i, url_full in enumerate(crawler.urls):
        parser = ArticleParser(full_url=url_full, article_id=i+1)
        parser.parse()
        parser.article.save_raw()
