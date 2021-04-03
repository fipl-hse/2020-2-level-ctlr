"""
Crawler implementation
"""
import json
import os
from time import sleep
from datetime import datetime
import random
import shutil
import requests
from bs4 import BeautifulSoup
from article import Article
from constants import CRAWLER_CONFIG_PATH
from constants import ASSETS_PATH



class IncorrectURLError(Exception):
    """
    Custom error
    """


class NumberOfArticlesOutOfRangeError(Exception):
    """
    Custom error
    """
class UnknownConfigError(Exception):
    """
    "General error"
    """

class IncorrectNumberOfArticlesError(Exception):
    """
    Custom error
    """
headers={
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        '(KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}



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
        url_article = article_bs.find('h3', class_='entry-title td-module-title').find('a')
        link = url_article.attrs['href']
        return link

    def find_articles(self):
        """
        Finds articles
        """
        for url in self.seed_urls:
            response = requests.get(url, headers=headers)
            if not response:
                raise IncorrectURLError
            if response.status_code == 200:
                sleep(random.randint(5, 10))
            seed_soup = BeautifulSoup(response.content, features='lxml')
            articles_soup = seed_soup.find_all('table', class_='item-details')
            for article_bs in articles_soup[:self.max_articles_per_seed]:
                self.urls.append(self._extract_url(article_bs))
                if len(self.urls) == self.max_articles:
                    break
        print (self.urls)

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
        self.article = Article(self.full_url, self.article_id)

    def _fill_article_with_text(self, article_soup):
        text = article_soup.find('div', class_="td-post-content td-pb-padding-side").find_all("p")
        clean_text = [sent.text for sent in text]
        self.article.text = " ".join(clean_text)

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find('h1', class_='entry-title').text.strip()
        self.article.author = 'NOT FOUND'
        date = article_soup.find(class_="meta-info").text.split(",")[0]
        self.article.date = ArticleParser.unify_date_format(date)

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format
        """
        months = {
            'января': 1,
            'февраля': 2,
            'марта': 3,
            'апреля': 4,
            'мая': 5,
            'июня': 6,
            'июля': 7,
            'августа': 8,
            'сентября': 9,
            'октября': 10,
            'ноября': 11,
            'декабря': 12,
        }
        date = date_str.split()
        date[1] = months[date[1]]
        date = datetime(int(date[2]), int(date[1]), int(date[0]))
        return date

    def parse(self):
        """
        Parses each article
        """
        response = requests.get(self.full_url, headers = headers)
        article_bs = BeautifulSoup(response.content, features='lxml')
        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if os.path.exists(base_path):
        shutil.rmtree(base_path)
    os.makedirs(base_path)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as file:
        config = json.load(file)
    if not isinstance(config, dict) or not 'base_urls' in config \
            or not 'total_articles_to_find_and_parse' in config:
        raise UnknownConfigError
    if not isinstance(config['base_urls'], list) or not all(isinstance(url, str) for url in config['base_urls']):
        raise IncorrectURLError
    if not isinstance(config['total_articles_to_find_and_parse'], int):
        raise IncorrectNumberOfArticlesError
    if config['total_articles_to_find_and_parse'] > 100:
        raise NumberOfArticlesOutOfRangeError
    return config.values()


if __name__ == '__main__':
    # YOUR CODE HERE
    urls, maximum_articles, maximum_articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    crawler = Crawler(urls, maximum_articles, maximum_articles_per_seed)
    articles = crawler.find_articles()
    prepare_environment(ASSETS_PATH)
    for ind, article_url in enumerate(crawler.urls):
        parser = ArticleParser(full_url=article_url, article_id=ind + 1)
        sleep(5)
        article = parser.parse()
        article.save_raw()
