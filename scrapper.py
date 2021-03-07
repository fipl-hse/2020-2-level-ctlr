"""
Crawler implementation
"""

import json
import re
import os
import shutil

from random import randint
from time import sleep
from datetime import datetime

import requests

from requests import HTTPError
from bs4 import BeautifulSoup

from constants import CRAWLER_CONFIG_PATH
from constants import PROJECT_ROOT
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
    def __init__(self, seed_urls: list, total_max_articles: int, max_articles_per_seed: int):
        self.seed_urls = seed_urls
        self.total_max_articles = total_max_articles
        self.max_articles_per_seed = max_articles_per_seed
        self.urls = []

    @staticmethod
    def _extract_url(article_bs):
        pass

    def find_articles(self):
        """
        Finds articles
        """
        headers = {'user-agent': "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) "
                                 "Chrome/88.0.4324.190 Safari/537.36"}
        for u in self.seed_urls:
            try:
                response = requests.get(u, headers=headers)
                page_soup = BeautifulSoup(response.content, 'lxml')
                news_container_id = 'MainMasterContentPlaceHolder_DefaultContentPlaceHolder_panelArticles'
                news_container = page_soup.find('div', attrs={'class': 'news-container', 'id': news_container_id})
                a_tags = news_container.find_all('a', id=re.compile('articleLink'))
                for a_tag in a_tags:
                    if len(self.urls) < self.max_articles_per_seed:
                        self.urls.append(a_tag.attrs['href'])
                    else:
                        break
            except HTTPError:
                print('Something wrong the URL...')
            if len(self.urls) < self.total_max_articles:
                sleep(randint(3, 6))
            else:
                break

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
        self.article.date = datetime.strptime(date_tag.text, "%d.%m.%Y")
        author_tag = article_soup.find('a', id='MainMasterContentPlaceHolder_InsidePlaceHolder_authorName')
        self.article.author = author_tag.text
        topic_tags = article_soup.find_all('a', id=re.compile('[cC]ategoryName'))
        self.article.topics = [topic_tag.text for topic_tag in topic_tags]

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format
        """
        pass

    def parse(self):
        """
        Parses each article
        """
        headers = {'user-agent': "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) "
                                 "Chrome/88.0.4324.190 Safari/537.36"}
        response = requests.get(self.full_url, headers=headers)
        article_bs = BeautifulSoup(response.content, 'lxml')
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
    with open(crawler_path) as json_file:
        config = json.load(json_file)

    urls = config['base_urls']
    total_artcls = config['total_articles_to_find_and_parse']
    max_artcls = config.get('max_number_articles_to_get_from_one_seed', total_artcls)

    is_url_ok = isinstance(urls, list) and all(isinstance(u, str) for u in urls)
    is_articles_num_ok = (isinstance(total_artcls, int) and not isinstance(total_artcls, bool) and
                          isinstance(max_artcls, int) and not isinstance(max_artcls, bool))

    if not is_url_ok:
        raise IncorrectURLError

    if not is_articles_num_ok:
        raise IncorrectNumberOfArticlesError

    is_articles_num_in_range = 0 < max_artcls <= total_artcls and 5 <= total_artcls <= 1000

    if not is_articles_num_in_range:
        raise NumberOfArticlesOutOfRangeError

    if is_url_ok and is_articles_num_ok and is_articles_num_in_range:
        return urls, total_artcls, max_artcls

    raise UnknownConfigError


if __name__ == '__main__':
    # YOUR CODE HERE
    url_list, total, max_num = validate_config(CRAWLER_CONFIG_PATH)
    crawler = Crawler(seed_urls=url_list, total_max_articles=total, max_articles_per_seed=max_num)
    crawler.find_articles()
    prepare_environment(PROJECT_ROOT)
    for i, url in enumerate(crawler.urls):
        parser = ArticleParser(full_url=url, article_id=i+1)
        article = parser.parse()
        article.save_raw()
        sleep(randint(3, 6))
