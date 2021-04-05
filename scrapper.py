"""
Crawler implementation
"""
import json
import os
import random
import re
import shutil
from time import sleep
from datetime import datetime

import requests
from bs4 import BeautifulSoup

import constants
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
    def __init__(self, seed_urls: list, max_articles: int, max_articles_per_seed: int):
        self.seed_urls = seed_urls
        self.max_articles = max_articles
        self.max_articles_per_seed = max_articles_per_seed
        self.urls = []

    @staticmethod
    def _extract_url(article_bs):
        container = article_bs.find('div', attrs={
            'id': 'MainMasterContentPlaceHolder_DefaultContentPlaceHolder_panelArticles'})
        tags = container.find_all('a', id=re.compile('_articleLink'))

        return [tag.attrs['href'] for tag in tags]

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.get_search_urls():
            response = requests.get(seed_url, headers=constants.HEADERS)
            sleep(random.randrange(2, 6))
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
        text = list()
        text.append(article_soup.find(
            'p', id='MainMasterContentPlaceHolder_InsidePlaceHolder_articleAnnotation').text)
        text.append(article_soup.find(
            'div', id='MainMasterContentPlaceHolder_InsidePlaceHolder_articleText').text)
        self.article.text = '\n'.join(text)

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find(
            'a', id='MainMasterContentPlaceHolder_InsidePlaceHolder_articleHeader').text
        self.article.author = article_soup.find(
            'a', id='MainMasterContentPlaceHolder_InsidePlaceHolder_authorName').text
        self.article.date = self.unify_date_format(article_soup.find(
            'time', id='MainMasterContentPlaceHolder_InsidePlaceHolder_articleTime').text)

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
        article_bs = BeautifulSoup(requests.get(self.full_url, headers=constants.HEADERS).content, 'lxml')
        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    assets_path = os.path.join(base_path, 'tmp', 'articles')
    if os.path.exists(assets_path):
        shutil.rmtree(os.path.dirname(assets_path))
    os.makedirs(assets_path)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as file:
        conf = json.load(file)

    url_check = re.compile(r"^(https?:\/\/)?moyaokruga.ru\/ahtpravda\/(\?([a-z]+id=([0-9]+)?&?)*)?", re.I)

    if not conf["base_urls"]:
        raise IncorrectURLError

    if not all(url_check.match(str(link)) for link in conf["base_urls"]):
        raise IncorrectURLError

    if not isinstance(conf["total_articles_to_find_and_parse"], int):
        raise IncorrectNumberOfArticlesError

    if conf["total_articles_to_find_and_parse"] <= 0 \
            or conf["total_articles_to_find_and_parse"] > 100:
        raise NumberOfArticlesOutOfRangeError

    return conf['base_urls'], conf['total_articles_to_find_and_parse'], conf[
        'max_number_articles_to_get_from_one_seed']


if __name__ == '__main__':
    # YOUR CODE HERE
    seed_urls_list, total_max_articles, max_articles_per_seed_num = validate_config(constants.CRAWLER_CONFIG_PATH)
    crawler = Crawler(seed_urls=seed_urls_list, max_articles=total_max_articles,
                      max_articles_per_seed=max_articles_per_seed_num)
    crawler.find_articles()
    prepare_environment(constants.PROJECT_ROOT)

    for i, url in enumerate(crawler.urls, 1):
        parser = ArticleParser(full_url=url, article_id=i)
        article = parser.parse()
        article.save_raw()
        sleep(random.randrange(2, 6))
