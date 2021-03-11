"""
Crawler implementation
"""
import requests
import random
import time
import re
import os
import json
import datetime
from article import Article
from constants import CRAWLER_CONFIG_PATH, ASSETS_PATH

headers = {'user-agent': {'Date': 'Mon, 22 Feb 2021 10:53:27 GMT', 'Server': 'Apache/2.4.18 (Ubuntu)',
                              'Set-Cookie': 'Lmldq-siA=ijAbUD; expires=Tue, 23-Feb-2021 10:53:27 GMT; Max-Age=86400; path=/, JEBRIhOYuTk_S=kH8Tvdr5c2BV; expires=Tue, 23-Feb-2021 10:53:27 GMT; Max-Age=86400; path=/, XEJb-x=NwOV1b; expires=Tue, 23-Feb-2021 10:53:27 GMT; Max-Age=86400; path=/, KWcatUPxVb_=z%2AsnxrVEW1m.4; expires=Tue, 23-Feb-2021 10:53:27 GMT; Max-Age=86400; path=/',
                              'Link': '<http://tomsk-novosti.ru/wp-json/>; rel="https://api.w.org/", <http://tomsk-novosti.ru/wp-json/wp/v2/posts/321365>; rel="alternate"; type="application/json", <http://tomsk-novosti.ru/?p=321365>; rel=shortlink',
                              'Vary': 'Accept-Encoding', 'Content-Encoding': 'gzip', 'Content-Length': '15069',
                              'Keep-Alive': 'timeout=5, max=100', 'Connection': 'Keep-Alive',
                              'Content-Type': 'text/html; charset=UTF-8'}
               }

class IncorrectURLError(Exception):
    """
    Custom error
    """
    def __init__(self, seed_urls: list, max_articles: int):
        self.seed_urls = seed_urls
        self.max_articles = max_articles
        self.max_articles_per_seed = max_articles_per_seed
        self.urls = []

    @staticmethod
    def _extract_url(article_bs):
        return article_bs.find('a').attrs['href']

    def find_articles(self):
        for url in self.seed_urls:
            responsee = requests.get(url, headers)
            page_content = responsee.content

            page_soup = BeautifulSoup(page_content, 'lxml')
            div_tag = page_soup.find('div', 'entry-content')
            urls = []
            a_soup = div_tag.find_all('a')
            for link in a_soup[:self.max_articles_per_seed]:
                urls.append(link.get('href'))
            urls_sliced = urls[1::2]
            urls_sliced = urls_sliced[:self.max_articles]

            new_urls = []
            for url in urls_sliced:
                new_urls.append('http://tomsk-novosti.ru/' + url)
            return new_urls

    def get_search_urls(self):
        return self.find_articles()


class Crawler:
    """
    Crawler implementation
    """
    def __init__(self, seed_urls: list, max_articles: int):
        self.seed_urls = seed_urls

    @staticmethod
    def _extract_url(article_bs):
        pass

    def find_articles(self):
        """
        Finds articles
        """
        for url in self.seed_urls:
            response = requests.get(url)
            time.sleep(5)
            print('Got requests')

        return []

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
        pass

    def _fill_article_with_text(self, article_soup):
        pass

    def _fill_article_with_meta_information(self, article_soup):
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
        pass


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    pass


def validate_config(crawler_path):
    """
    Validates given config
    """
    pass


if __name__ == '__main__':
    # YOUR CODE HERE
    pass

test = Crawler(['http://tomsk-novosti.ru/chto-za-tresh-a-draki-net/', 'http://tomsk-novosti.ru/tsifrovaya-zrelost/'])
test.find_articles()