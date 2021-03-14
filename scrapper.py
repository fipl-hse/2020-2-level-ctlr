"""
Crawler implementation
"""
import json
import os
from datetime import datetime
import re

import requests
from bs4 import BeautifulSoup
from time import sleep
import random

import article
from article import Article
from constants import PROJECT_ROOT
from constants import ASSETS_PATH
from constants import CRAWLER_CONFIG_PATH


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

    @staticmethod
    def _extract_url(self, article_bs):
        pass

    def find_articles(self):
        """
        Finds articles
        """
        headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML,'
                                 ' like Gecko) Chrome/88.0.4324.150 Safari/537.36'}
        for url in self.seed_urls:
            responsee = requests.get(url, headers=headers)
            page_content = responsee.content

            page_soup = BeautifulSoup(page_content, features='lxml')
            div_tag = page_soup.find('div', class_='news-list')
            urls = []
            a_soup = div_tag.find_all('a')
            for link in a_soup[:self.max_articles_per_seed]:
                urls.append(link.get('href'))
            urls_sliced = urls[1::2]
            urls_sliced = urls_sliced[:self.max_articles]

            new_urls = []
            for url in urls_sliced:
                new_urls.append('https://восход65.рф' + url)
            return new_urls

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        seed_urls = self.find_articles()
        return seed_urls


class ArticleParser:
    """
    ArticleParser implementation
    """

    def __init__(self, full_url: str, article_id: int):
        self.full_url = full_url
        self.article_id = article_id
        self.article = Article(self.full_url, self.article_id)

    def _fill_article_with_text(self, article_soup):
        self.article.text = article_soup.find(name='div', id="article").text
        # self.article.text = re.sub(' ', '&nbsp;', self.article.text)
        # self.article.text = re.sub('&nbsp;', ' ', self.article.text)
        # self.article.text = re.sub('­', ' ', self.article.text)

    def _fill_article_with_meta_information(self, article_soup):

        all_text = article_soup.find(name='div', id="article")
        categ_tag = all_text.find_all(name='p', class_="news-category")
        self.article.topics = categ_tag[0].text

        self.article.title = article_soup.find(name='title').text
        #h1_tag = all_text.find_all(name="h1")

        #self.article.title = h1_tag[0].text
        #self.article.title = re.sub(' ', '&nbsp;', self.article.title)

        #return None

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
        headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML,'
                                 ' like Gecko) Chrome/88.0.4324.150 Safari/537.36'}
        response = requests.get(self.full_url, headers=headers)
        page_content = response.content
        article_bs = BeautifulSoup(page_content, features='lxml')

        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        self.article.save_raw()




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
    with open(crawler_path, 'r', encoding='utf-8') as conf_file:
        config = json.load(conf_file)

    is_config_not_ok = ('base_urls' not in config
                         or 'total_articles_to_find_and_parse' not in config
                         or 'max_number_articles_to_get_from_one_seed' not in config)

    are_urls_not_ok = (not isinstance(config['base_urls'], list)
                       or not all([isinstance(url, str) for url in config['base_urls']]))

    is_num_not_ok = (not isinstance(config['total_articles_to_find_and_parse'], int)
                                 or config['total_articles_to_find_and_parse'] < 0)

    if not isinstance(config, dict) and is_config_not_ok:
        raise UnknownConfigError

    if are_urls_not_ok:
        raise IncorrectURLError

    if is_num_not_ok:
        raise IncorrectNumberOfArticlesError

    if config['total_articles_to_find_and_parse'] > 100:
        raise NumberOfArticlesOutOfRangeError

    return config.values()


if __name__ == '__main__':
    # YOUR CODE HERE
    seed_urls,  max_articles, max_articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)

    crawler = Crawler(seed_urls=seed_urls, max_articles=max_articles, max_articles_per_seed=max_articles_per_seed)
    urlss = crawler.find_articles()
    prepare_environment(ASSETS_PATH)

    for id, url in enumerate(urlss):
        parser = ArticleParser(url, id+1)
        parser.parse()




