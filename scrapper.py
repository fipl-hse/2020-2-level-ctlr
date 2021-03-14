"""
Crawler implementation
"""
import json
import os
from time import sleep
import requests
from bs4 import BeautifulSoup
from article import Article
from constants import CRAWLER_CONFIG_PATH, ASSETS_PATH

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
           'Chrome/89.0.4389.82 Safari/537.36'}


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
        self.max_articles_per_speed = max_articles_per_seed
        self.urls = []

    @staticmethod
    def _extract_url(article_bs):
        url_article = article_bs.find('a')
        return 'http://orbita-znamensk.ru/' + url_article.attrs['href']

    def find_articles(self):
        """
        Finds articles
        """
        for s_url in self.seed_urls:
            response = requests.get(s_url, headers=headers)
            sleep(5)
            if not response:
                raise IncorrectURLError
            article_bs = BeautifulSoup(response.content, features='lxml')
            links = article_bs.find_all('div', class_='title')
            for article in links:
                if len(self.urls) <= self.max_articles and article not in self.urls:
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
        self.article_url = full_url
        self.ids = article_id
        self.article = Article(full_url, article_id)

    def _fill_article_with_text(self, article_soup):
        paragraphs_soup = article_soup.find('div', class_='node-inner').find_all('p')
        for par in paragraphs_soup:
            self.article.text += par.text.strip() + '\n'

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find('h1').text.strip()
        return None

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format
        """

    def parse(self):
        """
        Parses each article
        """
        article_bs = BeautifulSoup(requests.get(self.article_url, headers=headers).content, 'lxml')
        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
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
    with open(crawler_path, 'r', encoding='utf-8') as file:
        crawler_config = json.load(file)

    if ('base_urls' not in crawler_config
            or not isinstance(crawler_config['base_urls'], list)
            or not all([isinstance(url, str) for url in crawler_config['base_urls']])):
        raise IncorrectURLError

    if ('total_articles_to_find_and_parse' in crawler_config and
            isinstance(crawler_config['total_articles_to_find_and_parse'], int)
            and crawler_config['total_articles_to_find_and_parse'] > 101):
        raise NumberOfArticlesOutOfRangeError

    if (not isinstance(crawler_config['total_articles_to_find_and_parse'], int)
            or 'total_articles_to_find_and_parse' not in crawler_config
            or 'max_number_articles_to_get_from_one_seed' not in crawler_config):
        raise IncorrectNumberOfArticlesError

    return (crawler_config['base_urls'],
            crawler_config['total_articles_to_find_and_parse'],
            crawler_config['max_number_articles_to_get_from_one_seed'])


if __name__ == '__main__':
    # YOUR CODE HERE
    seed_urls, max_articles, max_articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)

    crawler = Crawler(seed_urls, max_articles, max_articles_per_seed)
    crawler.find_articles()

    prepare_environment(ASSETS_PATH)

    for ind, article_url in enumerate(crawler.urls):
        parser = ArticleParser(full_url=article_url, article_id=ind + 1)
        sleep(5)
        article = parser.parse()
        article.save_raw()

