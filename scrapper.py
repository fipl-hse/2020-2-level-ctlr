"""
Crawler implementation
"""

from bs4 import BeautifulSoup
from random import randint
import re
import requests
from time import sleep

class IncorrectURLError(Exception):
    """
    Custom error
    """
    pass


class NumberOfArticlesOutOfRangeError(Exception):
    """
    Custom error
    """
    pass


class IncorrectNumberOfArticlesError(Exception):
    """
    Custom error
    """
    pass


class BadStatusCode(Exception):
    pass


class Crawler:
    """
    Crawler implementation
    """
    def __init__(self, seed_urls: list, max_articles: int = None):
        self.seed_urls = seed_urls
        self.seed_urls_set = set()
        self.max_articles = max_articles
        self.headers = headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                                '(KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'}
        self.article_urls = []

        for url in self.seed_urls:
            try:
                page = self.get_page(url)
            except BadStatusCode:
                continue
            else:
                soup = BeautifulSoup(page, 'html.parser')
                if len(self.article_urls) < self.max_articles:
                    self.find_articles(soup)
                self.get_search_urls(soup)
            self.seed_urls.pop(url)
        else:
            if len(self.article_urls) > max_articles:
                 with open('links.txt', 'w') as f:
                     f.write('\n'.join(self.article_urls[:max_articles]))

    @staticmethod
    def _extract_url(article_bs):
        pass

    def find_articles(self, soup):
        """
        Finds articles
        """
        new_links = []
        for link in soup.find_all('a'):
            if res := re.findall(r'https://www.zvezdaaltaya.ru/\d{4}/\d{2}/.+', link.get('href')):
                if not re.findall(r'https://www.zvezdaaltaya.ru/\d{4}/\d{2}/\d{2}/', res[0]):
                    if res[0] not in self.article_urls:
                        new_links.append(res[0])
        with open('links.txt', 'a') as f:
          f.write('\n'.join(new_links) + '\n')
        self.article_urls.extend(new_links)

    def get_search_urls(self, soup):
        """
        Returns seed_urls param
        """
        for link in soup.find_all('a'):
            if res := re.findall(r'https://www.zvezdaaltaya.ru/.+', link.get('href')):
                if res[0] not in self.seed_urls:
                    self.seed_urls.append(res[0])
                    self.seed_urls_set.add(res[0])


    def get_page(self, url):
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            page = response.text
        else:
            raise BadStatusCode
        sleep(randint(3, 10))
        return page


class ArticleParser:
    """
    ArticleParser implementfation
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
