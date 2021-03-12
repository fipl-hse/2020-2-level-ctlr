"""
Crawler implementation
"""
import json
import random
import re
from time import sleep

import requests
from bs4 import BeautifulSoup

from article import Article
from constants import CRAWLER_CONFIG_PATH

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'}

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
    Custom error
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
        pass

    def find_articles(self):
        """
        Finds articles
        """
        raw_urls_list = []
        total_counter = 0
        for url in self.seed_urls:
            response = requests.get(url, headers=headers)
            print('Making a request...')
            sleep_interval = random.randrange(2, 5)
            sleep(sleep_interval)
            article_bs = BeautifulSoup(response.content, features='lxml')
            link_sample = re.compile(r'/\d{6}.+')
            per_seed_counter = 0
            for link_container in article_bs.find_all(name='a'):
                link_itself = link_container.get('href')
                if re.match(link_sample, str(link_itself)) and str(link_itself) not in raw_urls_list:
                    raw_urls_list.append(link_itself)
                    total_counter += 1
                    per_seed_counter += 1
                    if self.total_max_articles == total_counter or self.max_articles_per_seed == per_seed_counter:
                        break
            if self.total_max_articles == total_counter:
                break
        for link in raw_urls_list:
            self.urls.append('https://www.infpol.ru' + link)



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
        self.article_url = full_url
        self.i = article_id
        self.article = Article(full_url, article_id)
        pass

    def _fill_article_with_text(self, article_soup):
        self.article.text = article_soup.find(name='div', class_='content')
        print(self.article.text)

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find(name='h1').text
        self.article.date = article_soup.find(name='time', class_='js-time').text
        self.article.author = article_soup.find(class_='author').text
        self.article.topics = []
        self.article.text = '\n'.join(abstract.text for abstract in article_soup.find_all(name='p'))

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
        response = requests.get(self.article_url, headers=headers)
        print('The webpage is being requested...')
        if response.status_code == 200:
            print('Request is OK')
        article_bs = BeautifulSoup(response.content, features='lxml')
        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        article.save_raw()
        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    pass


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r') as crawler:
        data = json.loads(str(crawler.read()))

    validating_seed_urls = data.get("base_urls")
    validating_max_articles = data.get("total_articles_to_find_and_parse")
    validating_max_articles_per_seed = data.get("max_number_articles_to_get_from_one_seed")

    if not isinstance(validating_seed_urls, list) or not isinstance(validating_max_articles, int)\
            or not isinstance(validating_max_articles_per_seed, int):
        raise UnknownConfigError

    for url in validating_seed_urls:
        if not re.match('https://www\.[\d\w-]+\..+', url):
            raise IncorrectURLError

    if validating_max_articles == 0:
        raise NumberOfArticlesOutOfRangeError

    if validating_max_articles_per_seed == 0:
        raise IncorrectNumberOfArticlesError
    return validating_seed_urls, validating_max_articles, validating_max_articles_per_seed


if __name__ == '__main__':
    seed_urls, max_articles, max_articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    example = Crawler(seed_urls, max_articles, max_articles_per_seed)
    example.find_articles()

    for url in example.urls:
        parser = ArticleParser(url, 1) #where to take id
        article = parser.parse()
        article.save_raw()

