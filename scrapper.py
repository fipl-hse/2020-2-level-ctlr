"""
Crawler implementation
"""
from bs4 import BeautifulSoup
import re
import requests
from time import sleep
import random
import json
import os
from article import Article
from constants import HEADERS
from constants import ASSETS_PATH
from constants import CRAWLER_CONFIG_PATH


class IncorrectURLError(Exception):
    """
    Custom error.
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
        raw_urls_list = []
        link_sample = re.compile(r'/\d{7}.+')
        for link_container in article_bs.find_all(name='a'):
            link_itself = link_container.get('href')
            if re.match(link_sample, str(link_itself)) and str(link_itself) not in raw_urls_list:
                raw_urls_list.append(link_itself)
        return raw_urls_list

    @property
    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.get_search_urls():
            try:
                response = requests.get(seed_url, headers=HEADERS)
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
        self.article_url = full_url
        self.i = article_id
        self.article = Article(full_url, article_id)

    def _fill_article_with_text(self, article_soup):
        paragraphs_soup = article_soup.find('div', class_='node-inner').find_all('p')
        for par in paragraphs_soup:
            self.article.text += par.text.strip() + '\n'

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find('h1').text.strip()

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
        response = requests.get(self.article_url, headers=HEADERS)
        article_soup = BeautifulSoup(response.content, features='lxml')
        self.article.text += self._fill_article_with_text(article_soup)
        self._fill_article_with_meta_information(article_soup)
        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if not os.path.isdir(base_path):
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
    urls, max_articles_num, max_articles_num_per_seed = validate_config(CRAWLER_CONFIG_PATH)

    crawler = Crawler(seed_urls=urls,
                      max_articles=max_articles_num,
                      max_articles_per_seed=max_articles_num_per_seed)
    links = crawler.find_articles

    prepare_environment(ASSETS_PATH)
    for i, url_full in enumerate(crawler.urls):
        parser = ArticleParser(full_url=url_full, article_id=i + 1)
        parser.parse()
        parser.article.save_raw()
