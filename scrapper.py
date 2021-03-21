"""
Crawler implementation
"""
import json
import os
import random
import requests

from bs4 import BeautifulSoup
from article import Article
from constants import CRAWLER_CONFIG_PATH, HEADERS, ASSETS_PATH
from time import sleep


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
        article_link = article_bs.find('h2', class_="G3ax").find('a').get('href')
        return 'https://www.e1.ru' + article_link

    def find_articles(self):
        """
        Finds articles
        """
        for url in self.seed_urls:
            response = requests.get(url, headers=HEADERS)
            if not response:
                raise IncorrectURLError
            if response.status_code == 200:
                sleep(random.randrange(2, 6))
            response.encoding = 'utf-8'
            page_soup = BeautifulSoup(response.content, features='lxml')
            article_soup = page_soup.find_all('article', class_="G3ajx")
            for article in article_soup:
                seed_url = self._extract_url(article)
                self.urls.append(seed_url)
                if len(self.urls) <= max_articles and article not in self.urls:
                    seed_url = self._extract_url(article)
                    self.urls.append(seed_url)

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
        article_text = article_soup.find('div', class_="F-af3").find_all('p')
        for par in article_text:
            self.article.text += par.text.strip() + '\n'

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find('h2', class_="CVq3 CVtb KHax").find('span').text
        self.article.annotation = article_soup.find('p', class_="CVq- KHaj1").find('span').text
        self.article.author = 'NOT FOUND'
        self.article.topics = article_soup.find('a', class_="CVrn CVtj KHak5").find('span').text
        self.article.date = article_soup.find('time', class_="HDkz").find('a').text

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
        response = requests.get(self.full_url, headers=HEADERS)
        if not response:
            raise IncorrectURLError

        article_soup = BeautifulSoup(response.text, 'lxml')
        self._fill_article_with_text(article_soup)
        self._fill_article_with_meta_information(article_soup)
        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if not os.path.exists(base_path):
        os.makedirs(base_path)


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

        if not isinstance(max_articles_per_seed, int) or max_articles_per_seed > 100:
            raise NumberOfArticlesOutOfRangeError

    except(IncorrectURLError, IncorrectNumberOfArticlesError, NumberOfArticlesOutOfRangeError) as error:
        raise error
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
    for article_id, article_url in enumerate(crawler.urls):
        parser = ArticleParser(article_url, article_id+1)
        article = parser.parse()
        article.save_raw()
