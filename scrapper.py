""""
Crawler implementation
"""
import json
import os
from time import sleep
import random
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from article import Article



HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/88.0.4324.111 YaBrowser/21.2.1.108 Yowser/2.5 Safari/537.36 '
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
        url = article_bs.contents[1]
        return url.get('href')

    def find_articles(self):
        """
        Finds articles
        """
        self.get_search_urls()
        for url in self.seed_urls:
            response = requests.get(str(url))
            if not response:
                raise IncorrectURLError
            if len(self.urls) < self.max_articles:
                self.urls.append(url)
            else:
                break
        return self.urls

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        default_url = self.seed_urls[0]
        page = requests.get(str(default_url))
        soup = BeautifulSoup(page.text, 'html.parser')

        populars = soup.findAll('div', {"class": "block"})

        soup = BeautifulSoup(str(populars), 'html.parser')

        a_list = soup.find_all('a')

        self.seed_urls = []
        for element in a_list:
            self.seed_urls.append(element.get("href"))


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
        for par in article_texts:
            self.article.text += par.text.strip() + ' '

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find('section', {"class": "articles-main"}).find('header').a.text

        # find topic
        self.article.topic = article_soup.find('section', {"class": "articles-main"}).find('article').p.text

        # find date
        self.article.date = article_soup.find('section', {"class": "articles-main"}).find('header').time.text

        # find author
        self.article.author = article_soup.find('div', {"id": "content"}).find('a', {"class": "red"}).text

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format: strftime("%Y-%m-%d %H:%M:%S")
        """
        date = '-'.join(date_str.split('.')[::-1])
        date_time = str(datetime.strptime(date, "%Y-%m-%d"))

        return datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")

    def parse(self):
        """
        Parses each article
        """
        response = requests.get(self.full_url, headers=HEADERS)
        if not response:
            raise IncorrectURLError
        article_soup = BeautifulSoup(response.content, features='lxml')
        self._fill_article_with_text(
            article_soup.find('div', {"id": "MainMasterContentPlaceHolder_InsidePlaceHolder_articleText"}))
        self._fill_article_with_meta_information(article_soup)

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
    with open(crawler_path, 'r', encoding='utf-8') as file:
        crawler = json.load(file)

    if 'base_urls' not in crawler or not isinstance(crawler['base_urls'], list) or \
            not all([isinstance(url, str) for url in crawler['base_urls']]):
        raise IncorrectURLError

    if 'total_articles_to_find_and_parse' in crawler and \
            isinstance(crawler['total_articles_to_find_and_parse'], int) and \
            crawler['total_articles_to_find_and_parse'] > 100:
        raise NumberOfArticlesOutOfRangeError

    if 'max_number_articles_to_get_from_one_seed' not in crawler or \
            not isinstance(crawler['max_number_articles_to_get_from_one_seed'], int) or \
            'total_articles_to_find_and_parse' not in crawler or \
            not isinstance(crawler['total_articles_to_find_and_parse'], int):
        raise IncorrectNumberOfArticlesError

    seed_urls = crawler['base_urls']
    max_articles = crawler['total_articles_to_find_and_parse']
    max_articles_per_seed = crawler['max_number_articles_to_get_from_one_seed']
    return seed_urls, max_articles, max_articles_per_seed


if __name__ == '__main__':
    import constants

    seed_urls1, max_articles1, max_articles_per_seed1 = validate_config(constants.CRAWLER_CONFIG_PATH)
    crawler1 = Crawler(seed_urls1, max_articles1, max_articles_per_seed1)
    urls1 = crawler1.find_articles()
    prepare_environment(constants.ASSETS_PATH)
    ARTICLE_ID = 0
    for article_url in urls1:
        ARTICLE_ID += 1
        parser = ArticleParser(article_url, ARTICLE_ID)
        sleep(random.randint(2, 4))
        article = parser.parse()
        article.save_raw()
