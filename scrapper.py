"""
Crawler implementation
"""

import constants

from time import sleep
import requests
from bs4 import BeautifulSoup
from article import Article
import json
import re
import os
import shutil
from random import randint
from datetime import datetime

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0'}


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
        news_id = 'MainMasterContentPlaceHolder_DefaultContentPlaceHolder_panelArticles'
        news_container = article_bs.find('div', attrs={'class': 'news-container', 'id': news_id})
        a_tags = news_container.find_all('a', id=re.compile('articleLink'))

        return [a_tag.attrs['href'] for a_tag in a_tags]

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            response = requests.get(seed_url, headers=headers)
            sleep(randint(2, 6))
            page_bs = BeautifulSoup(response.content, 'lxml')
            extracted_url = self._extract_url(page_bs)
            articles_we_need = self.max_articles - len(self.urls)
            if self.max_articles_per_seed <= articles_we_need:
                self.urls.extend(extracted_url[:self.max_articles_per_seed])
            else:
                self.urls.extend(extracted_url[:articles_we_need])
            if len(self.urls) == self.max_articles:
                break

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.urls


class ArticleParser:
    """
    ArticleParser implementation
    """

    def __init__(self, article_url: str, article_id: int):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(article_url, article_id)

    def _fill_article_with_text(self, article_soup):
        text_list = list()
        annotation_tag = article_soup.find('p', id='MainMasterContentPlaceHolder_InsidePlaceHolder_articleAnnotation')
        text_list.append(annotation_tag.text)
        text_tag = article_soup.find('div', id='MainMasterContentPlaceHolder_InsidePlaceHolder_articleText')
        text_list.append(text_tag.text)
        self.article.text = '\n'.join(text_list)

    def _fill_article_with_meta_information(self, article_soup):
        title_tag = article_soup.find('a', id='MainMasterContentPlaceHolder_InsidePlaceHolder_articleHeader')
        self.article.title = title_tag.text
        date_tag = article_soup.find('time', id='MainMasterContentPlaceHolder_InsidePlaceHolder_articleTime')
        self.article.date = self.unify_date_format(date_tag.text)
        author_tag = article_soup.find('a', id='MainMasterContentPlaceHolder_InsidePlaceHolder_authorName')
        self.article.author = author_tag.text

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

        response = requests.get(self.article_url, headers=headers)
        article_bs = BeautifulSoup(response.content, 'lxml')
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
    with open(crawler_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    if 'base_urls' not in config or not isinstance(config['base_urls'], list) or \
            not all([isinstance(url, str) for url in config['base_urls']]):
        raise IncorrectURLError

    if 'total_articles_to_find_and_parse' in config and \
            isinstance(config['total_articles_to_find_and_parse'], int) and \
            config['total_articles_to_find_and_parse'] > 100:
        raise NumberOfArticlesOutOfRangeError

    if 'max_number_articles_to_get_from_one_seed' not in config or \
            not isinstance(config['max_number_articles_to_get_from_one_seed'], int) or \
            'total_articles_to_find_and_parse' not in config or \
            not isinstance(config['total_articles_to_find_and_parse'], int):
        raise IncorrectNumberOfArticlesError

    return config['base_urls'], config['total_articles_to_find_and_parse'], config[
        'max_number_articles_to_get_from_one_seed']


if __name__ == '__main__':
    # YOUR CODE HERE

    list_seed_urls, max_num_articles, maximum_articles_per_seed = validate_config(constants.CRAWLER_CONFIG_PATH)

    crawler = Crawler(seed_urls=list_seed_urls, max_articles=max_num_articles,
                      max_articles_per_seed=maximum_articles_per_seed)
    crawler.find_articles()
    prepare_environment(constants.ASSETS_PATH)
    for i, full_url in enumerate(crawler.get_search_urls()):
        parser = ArticleParser(article_url=full_url, article_id=i + 1)
        article = parser.parse()
        article.save_raw()
        sleep(randint(3, 6))
