"""
Crawler implementation
"""
import json
import random
import re
import os

from datetime import datetime
from time import sleep
import requests
from bs4 import BeautifulSoup
from article import Article

from constants import CRAWLER_CONFIG_PATH
from constants import PROJECT_ROOT

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'}


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
        links_list = []
        soup_strings = article_bs.find_all(class_="penci-grid")
        links = re.findall(r'(\"https?://кан-чарас.рф/.+/")', str(soup_strings))
        for link in links:
            if link not in links_list:
                links_list.append(link)
        return links_list

    def find_articles(self):
        """
        Finds articles
        """
        raw_urls = []
        for url in self.seed_urls:
            response = requests.get(url, headers=headers)
            print('Making a request...')
            sleep(random.randrange(2, 5))
            articles_page = BeautifulSoup(response.content, 'lxml')
            links = self._extract_url(articles_page)
            raw_urls.extend(links)
        for url in raw_urls:
            self.urls.append(url)
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
        text_soup = article_soup.find('div', class_="inner-post-entry").find_all('p')
        text = ''
        for par in text_soup:
            if par.text:
                text += par.text.strip() + '\n'
        if " " in text:
            text = text.replace(" ", ' ')
        self.article.text = text[:-1]

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find('h1').text
        text_soup = article_soup.find('div', class_="inner-post-entry").find_all('p')
        self.article.author = (text_soup[-1]).text
        self.article.date = self.unify_date_format(article_soup.find('div', class_="post-box-meta-single").text)

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format
        """
        unified_date = datetime.strptime(date_str.strip(), "%d.%m.%Y")
        return unified_date

    def parse(self):
        """
        Parses each article
        """
        response = requests.get(self.article_url, headers=headers)
        if not response:
            raise IncorrectURLError

        article_bs = BeautifulSoup(response.content, 'lxml')
        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        self.article.save_raw()
        return self.article


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
    urls, maximum_articles, maximum_articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    crawler = Crawler(urls, maximum_articles, maximum_articles_per_seed)
    articles = crawler.find_articles()
    prepare_environment(PROJECT_ROOT)
    for art_id, art_url in enumerate(crawler.urls, 1):
        parser = ArticleParser(full_url=art_url, article_id=art_id)
        article_from_list = parser.parse()
        sleep(random.randrange(2, 5))
