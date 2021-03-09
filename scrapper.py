"""
Crawler implementation
"""

import re
import json
import os
import shutil
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from constants import CRAWLER_CONFIG_PATH
from constants import HEADERS
from constants import ASSETS_PATH
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
        self.all_urls = []

    @staticmethod
    def _extract_url(article_bs):
        links = []
        articles = article_bs.find_all(class_ = "pb-caption")
        for one_article in articles:
            links.extend(re.findall(r'/article/[\w+_]+[\w]+/', str(one_article)))
        for index, link in enumerate(links):
            links[index] = 'https://ugra-news.ru' + link
        return links

    def find_articles(self):
        """
        Finds articles
        """

        for one_url in self.seed_urls:
            response = requests.get(one_url, headers=HEADERS)
            article_bs = BeautifulSoup(response.content, features='lxml')
            links = self._extract_url(article_bs)
            self.all_urls.extend(links)

        return self.all_urls

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
        article_text = article_soup.find(name='div', class_ = "js-pict-titles").text
        article_text = re.sub(r'\s+', '', article_text)
        self.article.text = article_text

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find(name='h1').text
        for inf in article_soup.find_all(name='div', class_='after-ar'):
            href_name = re.search(r"\/authors\/\S+\/", str(inf))
            if href_name:
                self.article.author = inf.find('a', href=href_name.group(0)).text
            else:
                self.article.author = 'NOT FOUND'
        date = article_soup.find(name='span', class_='t-date').text
        self.article.date = self.unify_date_format(date)

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format
        """
        return datetime.strptime(date_str.strip(), "%d.%m.%Y")

    def parse(self):
        """
        Parses each article
        """
        print(self.full_url)
        response = requests.get(self.full_url, headers=HEADERS)
        article_bs = BeautifulSoup(response.content, features='lxml')
        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)

        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if os.path.exists(ASSETS_PATH):
        shutil.rmtree(os.path.dirname(ASSETS_PATH))
    os.makedirs(ASSETS_PATH)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as f:
        cr_config = json.load(f)
    if not isinstance(cr_config, dict) or not 'base_urls' in cr_config \
            or not 'total_articles_to_find_and_parse' in cr_config:
        raise UnknownConfigError
    if not isinstance(cr_config['base_urls'], list) or not all(isinstance(url, str) for url in cr_config['base_urls']):
        raise IncorrectURLError
    if not isinstance(cr_config['total_articles_to_find_and_parse'], int):
        raise IncorrectNumberOfArticlesError
    if cr_config['total_articles_to_find_and_parse'] > 100000:
        raise NumberOfArticlesOutOfRangeError
    return cr_config['base_urls'], cr_config['total_articles_to_find_and_parse'], \
           cr_config['max_number_articles_to_get_from_one_seed']




if __name__ == '__main__':
    # YOUR CODE HERE
    print(CRAWLER_CONFIG_PATH)
    urls, max_articles, articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)

    crawler = Crawler(seed_urls=urls, total_max_articles=max_articles, max_articles_per_seed=articles_per_seed)
    crawler.find_articles()
    prepare_environment(ASSETS_PATH)
    for i, url in enumerate(crawler.all_urls):
        parser = ArticleParser(full_url=url, article_id=i)
        article = parser.parse()
        print(article.author, article.title, article.text)
        article.save_raw()
