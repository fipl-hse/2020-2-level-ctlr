"""
Crawler implementation
"""
import datetime
import json
import os
import random
import shutil
from time import sleep

import requests
from bs4 import BeautifulSoup

from constants import CRAWLER_CONFIG_PATH, HEADERS, PROJECT_ROOT
from article import Article


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
        self.urls = []

    @staticmethod
    def _extract_url(article):
        urls = []

        main_news = article.find(class_="main-news")
        if main_news is not None:
            links = main_news.find_all("a")
            for link in links:
                urls.append(link.get("href"))
        return urls

    def find_articles(self):
        """
        Finds articles
        """
        try:
            for main_url in self.seed_urls:
                if len(self.urls) < self.max_articles:
                    req = requests.get(main_url, HEADERS)

                    article = BeautifulSoup(req.content, 'html.parser')

                    self.urls += Crawler._extract_url(article)

            self.urls = self.urls[:self.max_articles]
        except IncorrectURLError:
            print("incorrect url")
        except NumberOfArticlesOutOfRangeError:
            print("too many articles")
        except IncorrectNumberOfArticlesError:
            print("incorrect number of articles")
        except UnknownConfigError:
            print("error in configuration")


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
        text_from_soup = article_soup.find(class_="video-show").find_all("p")
        clean_text = [sent.text for sent in text_from_soup]
        self.article.text = " ".join(clean_text)

    def _fill_article_with_meta_information(self, article_soup):
        self.article.author = "NOT FOUND"
        self.article.title = article_soup.find("h1").text
        date = article_soup.find(class_="date-time").text.split(",")[0]
        self.article.date = ArticleParser.unify_date_format(date)
        self.article.topics = [i.text for i in article_soup.find(class_ = "tags").find_all("a")]

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format
        """
        ru_months = {
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
        date[1] = ru_months[date[1]]
        date = datetime.datetime(int(date[2]), int(date[1]), int(date[0]))
        return date


    def parse(self):
        """
        Parses each article
        """
        response = requests.get(self.full_url, headers=HEADERS)
        if not response:
            raise IncorrectURLError

        article_bs = BeautifulSoup(response.content, 'lxml')
        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    assets_path = os.path.join(base_path, 'tmp', 'articles')
    if os.path.exists(assets_path):
        shutil.rmtree(os.path.dirname(assets_path))
    os.makedirs(assets_path)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as file:
        conf = json.load(file)

    if not isinstance(conf, dict) or 'base_urls' not in conf or 'total_articles_to_find_and_parse' not in conf:
        raise UnknownConfigError

    if not isinstance(conf['base_urls'], list) or \
            not all([isinstance(seed_url, str) for seed_url in conf['base_urls']]) or\
            not all(['https://' in seed_url for seed_url in conf["base_urls"]]):
        raise IncorrectURLError

    if not isinstance(conf['total_articles_to_find_and_parse'], int):
        raise IncorrectNumberOfArticlesError

    if conf["total_articles_to_find_and_parse"] > 100:
        raise NumberOfArticlesOutOfRangeError

    return conf['max_number_articles_to_get_from_one_seed'], conf['total_articles_to_find_and_parse'], conf["base_urls"]


if __name__ == '__main__':
    _max_num_articles, _total_number, _seed_urls = validate_config(CRAWLER_CONFIG_PATH)

    crawler = Crawler(_seed_urls, _max_num_articles)

    crawler.find_articles()

    prepare_environment(PROJECT_ROOT)
    print("started collecting articles")
    for art_index, art_url in enumerate(crawler.urls, start=1):
        parser = ArticleParser(art_url, art_index)
        article_parsed = parser.parse()
        article_parsed.save_raw()
        sleep(random.randrange(1, 5))
