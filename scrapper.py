"""
Crawler implementation
"""
import requests
import json
from time import sleep
import random
from bs4 import BeautifulSoup
import os
import re
from article import Article
from constants import CRAWLER_CONFIG_PATH
from constants import ASSETS_PATH
headers = {
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 YaBrowser/21.2.2.102 Yowser/2.5 Safari/537.36'
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
        return article_bs.find('a').attrs['href']


    def find_articles(self):
        """
        Finds articles
        """
        for ttm in self.seed_urls:
            response = requests.get(urls, headers=headers)
            sleep(random.randrange(3, 6))
            if not response:
                raise IncorrectURLError
            soup = BeautifulSoup(response.content, features='lxml')
            links = soup.find_all('div', {'class': 'entry-summary'})
            urls_number = min(articles_per_seed, len(links), (max_articles - len(self.urls)))
            for index in range(urls_number):
                self.urls.append('https://севернаяправда.рф/' + self._extract_url(article_bs=links[index]))
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
        self.full_url = full_url
        self.article_id = article_id
        self.article = Article(full_url, article_id)


    def _fill_article_with_text(self, article_soup):
        article_texts = article_soup.find_all('p')
        filling_article = []
        for texts in article_texts:
            if 'class' not in texts.attrs:
                filling_article.append(texts.text.strip())
        self.article.text = ' '.join(filling_article)


    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find('h1', class_="entry-title").text
        self.article.author = 'NOT FOUND'
        for topic in article_soup.find_all('a', rel="tag"):
            self.article.topics.append(topic.text)
        self.article.date = self.unify_date_format(article_soup.find('span', class_='date updated').text)


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
        response = BeautifulSoup(requests.get(self.full_url, headers=headers).content, 'lxml')
        if not response:
            raise IncorrectURLError
        article_soup = BeautifulSoup(response.content, features='lxml')
        self._fill_article_with_text(article_soup)
        self._fill_article_with_meta_information(article_soup)
        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if not os.path.exists(base_path):
        os.makedirs(base_path)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as file:
        crawler_config = json.load(file)
    for base_url in crawler_config['base_urls']:
        if not re.match('https://', base_url):
            raise IncorrectURLError
    if 'total_articles_to_find_and_parse' in crawler_config and \
            isinstance(crawler_config['total_articles_to_find_and_parse'], int) and \
            crawler_config['total_articles_to_find_and_parse'] > 100:
        raise NumberOfArticlesOutOfRangeError
    if not isinstance(crawler_config['total_articles_to_find_and_parse'], int):
        raise IncorrectNumberOfArticlesError
    return crawler_config['base_urls'], crawler_config['total_articles_to_find_and_parse'], \
           crawler_config['max_number_articles_to_get_from_one_seed']






if __name__ == '__main__':
    prepare_environment(ASSETS_PATH)
    urls, max_articles, articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    crawler = Crawler(seed_urls=urls, max_articles=max_articles, max_articles_per_seed=articles_per_seed)
    crawler.find_articles()

    for i, url in enumerate(crawler.urls):
        parser = ArticleParser(full_url=url, article_id=i + 1)
        parser.parse()