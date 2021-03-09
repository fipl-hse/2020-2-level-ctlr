"""
Crawler implementation
"""
import json
import requests
import os
import shutil
import random
import re
import constants

from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime
from article import Article


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/88.0.4324.182 Safari/537.36'}


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
        pass

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            response = requests.get(seed_url, headers=headers)
            sleep(random.randrange(2,6))
            page_bs = BeautifulSoup(response.content, 'lxml')
            container = page_bs.find('div', attrs={'class': 'news-container', 'id':
                'MainMasterContentPlaceHolder_DefaultContentPlaceHolder_panelArticles'})
            tags = container.find_all('a', id=re.compile('_articleLink'))  # можно заменять циферки (ctl01_ctl00) в id... или взять все теги с "articleLink"
            # id="MainMasterContentPlaceHolder_DefaultContentPlaceHolder_ctl01_ctl00_articleLink"
            articles_per_seed = 0
            for tag in tags:
                if articles_per_seed < self.max_articles_per_seed and len(self.urls) < self.max_articles:
                    self.urls.append(tag.attrs['href'])
                    articles_per_seed += 1


    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        pass


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
        article_bs = BeautifulSoup(requests.get(self.full_url, headers=headers).content, 'lxml')
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

    if not isinstance(conf, dict) or 'base_urls' not in conf or\
            'max_number_articles_to_get_from_one_seed' not in conf or\
            'total_articles_to_find_and_parse' not in conf:
        raise UnknownConfigError

    if not isinstance(conf['base_urls'], list) or\
            not all([isinstance(url,str) for url in conf['base_urls']]):
        raise IncorrectURLError

    if not isinstance(conf['total_articles_to_find_and_parse'], int) or \
            not isinstance(conf['max_number_articles_to_get_from_one_seed'], int):
        raise IncorrectNumberOfArticlesError

    if conf['max_number_articles_to_get_from_one_seed'] < 0:
        raise NumberOfArticlesOutOfRangeError

    return conf['base_urls'], conf['total_articles_to_find_and_parse'], conf['max_number_articles_to_get_from_one_seed']


if __name__ == '__main__':
    # YOUR CODE HERE
    prepare_environment(constants.PROJECT_ROOT)
    seed_urls, max_articles, max_articles_per_seed = validate_config(constants.CRAWLER_CONFIG_PATH)
    crawler = Crawler(seed_urls=seed_urls, max_articles=max_articles, max_articles_per_seed=max_articles_per_seed)
    crawler.find_articles()

    for i, url in enumerate(crawler.urls):
        parser = ArticleParser(full_url=url, article_id=i)
        article = parser.parse()
        article.save_raw()
        sleep(random.randrange(2,6))
