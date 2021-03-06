"""
Crawler implementation
"""
import requests
from bs4 import BeautifulSoup
from time import sleep
import random
from constants import PROJECT_ROOT, ASSETS_PATH, CRAWLER_CONFIG_PATH


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

    def __init__(self, seed_urls: list, max_articles: int):
        self.seed_urls = seed_urls
        self.max_articles = max_articles
        self.max_articles_per_seed = max_articles_per_seed
        self.headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML,'
                                      ' like Gecko) Chrome/88.0.4324.150 Safari/537.36'}

    @staticmethod
    def _extract_url(self, article_bs):
        responsee = requests.get(article_bs, headers=self.headers)
        return responsee

    def find_articles(self):
        """
        Finds articles
        """
        page_content = self._extract_url().content
        page_soup = BeautifulSoup(page_content, features='lxml')
        div_tag = page_soup.find('div', class_='news-list')
        urls = []
        for link in div_tag.find_all('a'):
            url = link.get('href')
            urls.append(url)
        urls = urls[1:10:2]
        return urls

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        seed_urls = []
        urls = self.find_articles()
        for url in urls:
            new_url = 'восход65.рф' + url
            seed_urls.append(new_url)
        return seed_urls




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


seed_urls, max_articles, max_articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)

if __name__ == '__main__':
    # YOUR CODE HERE
    pass
