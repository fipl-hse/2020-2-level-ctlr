"""
Crawler implementation
"""

import json
import random
import os

from datetime import datetime
from time import sleep
import requests
from bs4 import BeautifulSoup
from article import Article

from constants import CRAWLER_CONFIG_PATH
from constants import ASSETS_PATH

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/88.0.4324.111 YaBrowser/21.2.1.107 Yowser/2.5 Safari/537.36'}

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


class Crawler:
    """
    Crawler implementation
    """
    def __init__(self, seed_urls: list, max_article: int, max_articles_per_seed: int):
        self.seed_urls = seed_urls
        self.max_article = max_article
        self.max_articles_per_seed = max_articles_per_seed
        self.urls = []

    @staticmethod
    def _extract_url(article_bs):
        return article_bs.find('a').get('href')

    def find_articles(self):
        """
        Finds articles
        """
        for url in self.seed_urls:
            response = requests.get(url, headers=headers)
            sleep(random.randint(3, 7))
            if not response:
                raise IncorrectURLError
            page_soup = BeautifulSoup(response.content, features='lxml')
            article_soup = page_soup.find_all('div', class_='article-info')
            for article_bs in article_soup[:self.max_articles_per_seed]:
                self.urls.append(self._extract_url(article_bs))
                if len(self.urls) == self.max_article:
                    break
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
        article_text = []
        main_text = article_soup.find('div', class_="entry-content").find_all('p')
        article_text.append(main_text.text)
        self.article.text = '\n'.join(article_text)
        return None

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find('h1', class_='entry-title').text
        self.article.date = self.unify_date_format(article_soup.find('span', class_="entry-meta").text)
        text_soup = article_soup.find('div', class_="inner-post-entry").find_all('p')
        self.article_author = (text_soup[-1]).text

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
        response = requests.get(self.full_url, headers=headers)
        if not response:
            raise IncorrectURLError
        article_soup = BeautifulSoup(response.content, features='lxml')
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
    with open(crawler_path, 'r', encoding='utf-8') as file:
        conf = json.load(file)

    is_conf_unknown = ('base_urls' not in conf
                       or 'total_articles_to_find_and_parse' not in conf
                       or 'max_number_articles_to_get_from_one_seed' not in conf)

    if not isinstance(conf, dict) and is_conf_unknown:
        raise UnknownConfigError

    are_urls_incorrect = (not isinstance(conf['base_urls'], list)
                          or not all([isinstance(url, str) for url in conf['base_urls']]))

    if are_urls_incorrect:
        raise IncorrectURLError

    is_num_articles_incorrect = (not isinstance(conf['total_articles_to_find_and_parse'], int)
                                 or conf['total_articles_to_find_and_parse'] < 0)

    if is_num_articles_incorrect:
        raise IncorrectNumberOfArticlesError

    is_num_out_of_range = (conf['total_articles_to_find_and_parse'] > 100)
    if is_num_out_of_range:
        raise NumberOfArticlesOutOfRangeError

    return conf.values()


if __name__ == '__main__':
    # YOUR CODE HERE
    urls, max_articles, max_articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    crawler = Crawler(urls, max_articles, max_articles_per_seed)
    articles = crawler.find_articles()
    prepare_environment(ASSETS_PATH)
    for ind, article_url in enumerate(crawler.urls):
        parser = ArticleParser(full_url=article_url, article_id=ind)
        article = parser.parse()
        article.save_raw()
        sleep(random.randrange(3, 5))