"""
Crawler implementation
"""
import json
import os
import requests

from datetime import datetime
from bs4 import BeautifulSoup
from article import Article
from constants import CRAWLER_CONFIG_PATH
from constants import HEADERS
from constants import ASSETS_PATH
from time import sleep
import random


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
        self.total_max_articles = max_articles
        self.max_articles_per_seed = max_articles_per_seed

        self.urls = []

    @staticmethod
    def _extract_url(article_bs):
        article_link = article_bs.find('h2', {'itemprop': 'name'}).find('a').get('href')
        print(article_link)

    def find_articles(self):
        """
        Finds articles
        """
        for url in self.seed_urls:
            sleep(random.randint(2, 8))
            response = requests.get(url, headers=HEADERS)
            if not response:
                continue
            link = BeautifulSoup(response.content, features='lxml')
            articles_soup = link.find_all('li')
            for article_bs in articles_soup[:max_articles_per_seed]:
                self.urls.append(self._extract_url(article_bs))
                if len(self.urls) == max_articles:
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

    def _fill_article_with_text(self, article_soup):
        article_text = article_soup.find_all('p')
        for par in article_text:
            if 'class' not in par.attrs:
                self.article.text += par.text.strip() + ' '

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find('div',class_='page-header').find('h2').text
        self.article.views = article_soup.find('dd', class_="hits").find('meta').text
        self.article.date = self.unify_date_format(article_soup.find('dd', class_="create").find('time').text)
        self.article.author = 'NOT FOUND'

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format
        """
        return datetime.strptime(date_str, "%Y-%m-%d")

    def parse(self):
        """
        Parses each article
        """
        response = requests.get(self.full_url, headers=HEADERS)
        article_soup = BeautifulSoup(response.content, features='lxml')
        self._fill_article_with_text(article_soup)
        self._fill_article_with_meta_information(article_soup)
        self.article.save_raw()


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if not os.path.exists(os.path.join(base_path, 'tmp', 'articles')):
        os.makedirs(os.path.join(base_path, 'tmp', 'articles'))

def validate_config(crawler_path):
    """
    Validates given config
    """
    try:
        with open(crawler_path, 'r', encoding='utf-8') as config:
            params = json.load(config)

        seed_urls = params.get('base_urls')
        max_articles = params.get('total_articles_to_find_and_parse')
        max_articles_per_seed = params.get('max_number_articles_to_get_from_one_seed')

        if not isinstance(seed_urls, list):
            raise IncorrectURLError
        for url in seed_urls:
            if not isinstance(url, str) or not url.startswith('http'):
                raise IncorrectURLError

        if not isinstance(max_articles, int) or max_articles < 0:
            raise IncorrectNumberOfArticlesError

        if max_articles_per_seed > 100:
            raise NumberOfArticlesOutOfRangeError

    except(IncorrectURLError, IncorrectNumberOfArticlesError, NumberOfArticlesOutOfRangeError) as error:
        raise error
    except:
        raise UnknownConfigError
    else:
        return seed_urls, max_articles, max_articles_per_seed


if __name__ == '__main__':
    #YOUR CODE HERE
    seed_urls, max_articles, max_articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    crawler = Crawler(seed_urls=seed_urls,
                      max_articles=max_articles,
                      max_articles_per_seed=max_articles_per_seed)
    crawler.find_articles()

    prepare_environment(ASSETS_PATH)
    for i, url in enumerate(crawler.urls):
        parser = ArticleParser(full_url=url, article_id=i)
        parser.parse()
