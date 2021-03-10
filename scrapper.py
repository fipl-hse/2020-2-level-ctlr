"""
Crawler implementation
"""

import json
import datetime
import os
import shutil
import requests
from bs4 import BeautifulSoup
import article
from constants import CRAWLER_CONFIG_PATH
from constants import ASSETS_PATH

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/88.0.4324.190 Safari/537.36'
}


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
        self.urls = []

    @staticmethod
    def _extract_url(article_bs):
        url_article = article_bs.find('div', class_='article-link').find('a')
        link = url_article.attrs['href']
        return 'https://newbur.ru' + link

    def find_articles(self):
        """
        Finds articles
        """
        for url in self.seed_urls:
            response = requests.get(url, headers=headers)
            if not response:
                raise IncorrectURLError
            page_soup = BeautifulSoup(response.content, features='lxml')
            links = self._extract_url(page_soup)
            if len(links) < self.max_articles_per_seed:
                self.urls.extend(links)
            else:
                self.urls.extend(links[:self.max_articles_per_seed])

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
        self.article = article.Article(full_url, article_id)

    def _fill_article_with_text(self, article_soup):
        paragraphs_soup = article_soup.find_all('p')
        for parag in paragraphs_soup:
            self.article.text += parag.text.strip() + ''

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find('h1').text

        self.article.author = article_soup.find('div', class_='news-tags').find('a').text

        self.article.topics = article_soup.find('div', class_='article-details-left')\
            .find('a', class_='article-section')

        date = article_soup.find('div', class_='article-details-left').find('a', class_='article-date')
        self.article.date = self.unify_date_format(date)

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format
        """
        return datetime.datetime.strftime(date_str, '%d.%m.%Y')

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
        self.article.save_raw()
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
    with open(crawler_path, 'r', encoding='utf-8') as file:
        config = json.load(file)

    unknown = ('base_urls' not in config or 'total_articles_to_find_and_parse' not in config
               or 'max_number_articles_to_get_from_one_seed' not in config)
    if not isinstance(config, dict) and unknown:
        raise UnknownConfigError

    if not isinstance(config['base_urls'], list) or \
            not all(isinstance(url, str) for url in config['base_urls']):
        raise IncorrectURLError

    if 'total_articles_to_find_and_parse' in config and \
            isinstance(config['total_articles_to_find_and_parse'], int) and \
            config['total_articles_to_find_and_parse'] > 100:
        raise NumberOfArticlesOutOfRangeError

    if 'max_number_articles_to_get_from_one_seed' not in config or \
            not isinstance(config['max_number_articles_to_get_from_one_seed'], int) or \
            'total_articles_to_find_and_parse' not in config or \
            not isinstance(config['total_articles_to_find_and_parse'], int):
        raise IncorrectNumberOfArticlesError
    return config.values()


if __name__ == '__main__':
    # YOUR CODE HERE
    seed_urls_ex, max_articles_ex, max_articles_per_seed_ex = validate_config(CRAWLER_CONFIG_PATH)
    crawler = Crawler(seed_urls_ex, max_articles_ex, max_articles_per_seed_ex)
    crawler.find_articles()
    prepare_environment(ASSETS_PATH)
    for ind, article_url in enumerate(crawler.urls):
        parser = ArticleParser(full_url=article_url, article_id=ind)
        parser.parse()
