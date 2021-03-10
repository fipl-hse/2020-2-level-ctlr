"""
Crawler implementation
"""
import requests
import json
import os
from article import Article
from time import sleep
from random import randint
from bs4 import BeautifulSoup
from constants import CRAWLER_CONFIG_PATH
from constants import PROJECT_ROOT
from constants import ASSETS_PATH

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/88.0.4324.190 Safari/537.36'}


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
        self.max_articles_per_speed = max_articles_per_seed
        self.urls = []

    @staticmethod
    def _extract_url(article_bs):
        pass

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            response = requests.get(seed_url, headers=headers)
            sleep(randint(3, 7))
            response.encoding = 'utf-8'
            page_soup = BeautifulSoup(response.content, features='lxml')
            articles = page_soup.find_all('h3', class_='entry-title')
            page_links = []
            for article in articles:
                link = article.find("a").get("href")
                page_links.append(link)
        return []

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
        article_text_list = []
        text_soup = article_soup.find('div', class_='entry-content')
        main_text = text_soup.fins_all('p')
        for par in main_text:
           article_text_list.append(par.text)
        self.article.text = '\n'.join(article_text_list)

    def _fill_article_with_meta_information(self, article_soup):
        title = article_soup.find('h1')
        self.article.title = title.text

        date_soup = article_soup.find('div', class_='entry-meta')
        date = re.findall(r'\d.{9}', str(date_soup))
        self.article.date = date

        self.article.author = 'AUTHOR NOT FOUND'

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
    with open(crawler_path) as file:
        crawler_config = json.load(file)

    if ('base_urls' not in crawler_config
            or not isinstance(crawler_config['base_urls'], list)
            or not all([isinstance(url, str) for url in crawler_config['base_urls']])):
        raise IncorrectURLError

    if ('total_articles_to_find_and_parse' not in crawler_config or
            not isinstance(crawler_config['total_articles_to_find_and_parse'], int)
            or 'max_number_articles_to_get_from_one_seed' not in crawler_config
            or not isinstance(crawler_config['max_number_articles_to_get_from_one_seed'], int)):
        raise IncorrectNumberOfArticlesError

    if (crawler_config['max_number_articles_to_get_from_one_seed'] < 1
            or crawler_config['total_articles_to_find_and_parse'] < 1):
        raise NumberOfArticlesOutOfRangeError

    return (crawler_config['base_urls'],
            crawler_config['total_articles_to_find_and_parse'],
            crawler_config['max_number_articles_to_get_from_one_seed'])


if __name__ == '__main__':
    urls_list, max_articles_num, max_articles_num_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    crawler = Crawler(seed_urls=urls_list,
                      max_articles=max_articles_num,
                      max_articles_per_seed=max_articles_num)
    crawler.find_articles()

    for id, url in enumerate(crawler.get_search_urls()):
        parser = ArticleParser(full_url=url, article_id=id)
        parser.parse()
