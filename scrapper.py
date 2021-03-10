"""
Crawler implementation
"""
import json
import os

import requests
from bs4 import BeautifulSoup
from time import sleep
import random

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
            # print(new_urls)
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
        all_text = article_soup.find(name='div', id='article')
        text = str(all_text)
        return text

    def _fill_article_with_meta_information(self, article_soup):
        '''categ_tag = self._fill_article_with_text(article_soup).find_all(name='p', class_='news-category')
        category = categ_tag[0].text

        h1_tag = self._fill_article_with_text(article_soup).find_all(name='h1')
        title = h1_tag[0].text

        date_tag = self._fill_article_with_text(article_soup).find_all(name='p', class_='date')
        date = date_tag[0].text

        em_tag = self._fill_article_with_text(article_soup).find_all(name='em')
        if len(em_tag) == 1:
            author = em_tag[0].text
        else:
            author = 'NOT FOUND'
        return None'''
        pass

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
    with open(crawler_path, 'r', encoding='utf-8') as conf_file:
        conf = json.load(conf_file)

    urls = conf["base_urls"]
    total_art = conf["total_articles_to_find_and_parse"]

    is_total_not_ok = not isinstance(total_art, int) or total_art < 0
    is_config = ('base_urls' not in conf
                         or 'total_articles_to_find_and_parse' not in conf
                         or 'max_number_articles_to_get_from_one_seed' not in conf)

    if not isinstance(conf, dict) and is_config:
        raise UnknownConfigError

    if not isinstance(urls, list) or \
            (not isinstance(url, str) for url in urls):
        raise IncorrectURLError

    if total_art > 1000000:
        raise NumberOfArticlesOutOfRangeError

    if is_total_not_ok:
        raise IncorrectNumberOfArticlesError

    return urls, total_art




if __name__ == '__main__':
    # YOUR CODE HERE
    seed_urls, max_articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    urls = ['https://xn--65-dlci3cau6a.xn--p1ai/news/events/1/' ,'https://xn--65-dlci3cau6a.xn--p1ai/news/events/2/']

    crawler = Crawler(seed_urls=urls, max_articles=5, max_articles_per_seed=10)
    urls = crawler.find_articles()
    prepare_environment(ASSETS_PATH)
    article_id = 0
    for article_url in urls:
        article_id += 1
        parser = ArticleParser(article_url, article_id)
        article = parser.parse()
        article.save_raw()
