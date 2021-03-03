"""
Crawler implementation
"""
import article
import datetime
import json
import os
import random
import re
import requests

from bs4 import BeautifulSoup
from constants import CRAWLER_CONFIG_PATH
from constants import PROJECT_ROOT
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


class BadStatusCode(Exception):
    """
    Custom error
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
        soup_strings = article_bs.find_all(class_="block-content")
        links = re.findall(r'(\"https://astravolga.ru/(\w+[-])+\w+/")', str(soup_strings))
        return links

    def find_articles(self):
        """
        Finds articles
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74'}
        for url in self.seed_urls:
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    sleep(random.randrange(3, 6))
                    soup_menu_page = BeautifulSoup(response.content, 'lxml')
                else:
                    raise BadStatusCode
            except BadStatusCode:
                continue
            else:
                links = self._extract_url(soup_menu_page)
                articles_per_one_seed = 0
                for link in links:
                    if articles_per_one_seed >= self.max_articles_per_seed or len(self.urls) >= self.total_max_articles:
                        continue
                    else:
                        articles_per_one_seed += 1
                        self.urls.append(link[0][1:-2])
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
    def __init__(self, article_url: str, article_id: int):
        self.article_url = article_url
        self.article_id = article_id
        self.article = article.Article(article_url, article_id)

    def _fill_article_with_text(self, article_soup):
        text_soup = article_soup.find('div', class_="entry-content").find_all('p')
        text = ''
        for par in text_soup:
            if par.text:
                text += par.text.strip() + '\n'
        if " " in text:
            text = text.replace(" ", ' ')
        self.article.text = text[:-1]

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find('h1').text
        self.article.author = article_soup.find('div', class_="title-post").find(rel='author').text
        self.article.date = self.unify_date_format(article_soup.find('div', class_="title-post").find('li').text)

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format
        """
        date = datetime.datetime(int(re.findall(r'\d{4}', date_str)[0]),
                                 int(re.findall(r'\.(\d{2})\.', date_str)[0]),
                                 int(re.findall(r'^\d{2}', date_str)[0]),
                                 int(re.findall(r'(\d{1,2}):', date_str)[0]),
                                 int(re.findall(r':(\d{1,2})', date_str)[0]))
        return date

    def parse(self):
        """
        Parses each article
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74'}
        response = requests.get(self.article_url, headers=headers)
        if response:
            article_bs = BeautifulSoup(response.content, 'lxml')
            self._fill_article_with_text(article_bs)
            self._fill_article_with_meta_information(article_bs)
        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if os.path.exists(os.path.join(base_path, 'tmp', 'articles')):
        for root, dirs, files in os.walk(os.path.join(base_path, 'tmp', 'articles'), topdown=False):
            if files:
                for name in files:
                    os.remove(os.path.join(root, name))
    else:
        os.makedirs(os.path.join(base_path, 'tmp', 'articles'))


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as file:
        conf = json.load(file)
    if not isinstance(conf, dict) or 'base_urls' not in conf or \
            'max_number_articles_to_get_from_one_seed' not in conf or 'total_articles_to_find_and_parse' not in conf:
        raise UnknownConfigError
    if not isinstance(conf['base_urls'], list) or \
            not all([isinstance(seed_url, str) for seed_url in conf['base_urls']]):
        raise IncorrectURLError
    if not isinstance(conf['total_articles_to_find_and_parse'], int) or \
            not isinstance(conf['max_number_articles_to_get_from_one_seed'], int):
        raise TypeError
    if conf['total_articles_to_find_and_parse'] < 0:
        raise IncorrectNumberOfArticlesError
    if conf['max_number_articles_to_get_from_one_seed'] < 0 or \
            conf['max_number_articles_to_get_from_one_seed'] > conf['total_articles_to_find_and_parse']:
        raise NumberOfArticlesOutOfRangeError
    return conf['base_urls'], conf['total_articles_to_find_and_parse'], conf['max_number_articles_to_get_from_one_seed']


if __name__ == '__main__':
    # YOUR CODE HERE
    prepare_environment(PROJECT_ROOT)
    urls, max_articles, articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    crawler = Crawler(seed_urls=urls,
                      total_max_articles=max_articles,
                      max_articles_per_seed=articles_per_seed)
    articles = crawler.find_articles()
    for i, full_url in enumerate(crawler.urls, 1):
        parser = ArticleParser(article_url=full_url, article_id=i)
        article_from_list = parser.parse()
        article_from_list.save_raw()
        sleep(random.randrange(3, 6))
