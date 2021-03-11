"""
Crawler implementation
"""
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
    def __init__(self, main_urls, num_articles, max_articles, headers):
        self.main_urls = main_urls
        self.num_articles = num_articles
        self.max_articles = max_articles
        self.urls = []
        self.headers = headers

    @staticmethod
    def _extract_url(article_bs, headers):
        urls = []

        req = requests.get(article_bs, headers)
        main_article = BeautifulSoup(req.content, 'html.parser')
        main_news = main_article.find(class_="main-news")
        for link in main_news.find_all("a"):
            urls.append(link.get("href"))
        return urls

    def find_articles(self):
        """
        Finds articles
        """
        try:
            for main_url in self.main_urls:
                if len(self.urls) <= self.max_articles:
                    self.urls += Crawler._extract_url(main_url, self.headers)
        except IncorrectURLError:
            print("incorrect url")
        except NumberOfArticlesOutOfRangeError:
            print("too many articles")
        except IncorrectNumberOfArticlesError:
            print("incorrect number of articles")
        except UnknownConfigError:
            print("error in configuration") 
        self.urls = self.urls[:self.max_articles + 1]


    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.main_urls


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
        clean_text = [str(sent)[3:-4] for sent in text_from_soup]
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

    if not isinstance(conf, dict) or 'base_urls' not in conf or \
            'max_number_articles_to_get_from_one_seed' not in conf or 'total_articles_to_find_and_parse' not in conf:
        raise UnknownConfigError

    if not isinstance(conf['base_urls'], list) or \
            not all([isinstance(seed_url, str) for seed_url in conf['base_urls']]):
        raise IncorrectURLError

    if not isinstance(conf['total_articles_to_find_and_parse'], int) or \
            not isinstance(conf['max_number_articles_to_get_from_one_seed'], int):
        raise TypeError

    if conf['total_articles_to_find_and_parse'] < 0:
        raise IncorrectNumberOfArticlesError

    if conf['max_number_articles_to_get_from_one_seed'] < 0 or \
            conf['max_number_articles_to_get_from_one_seed'] > conf['total_articles_to_find_and_parse']:
        raise NumberOfArticlesOutOfRangeError

    return conf['max_number_articles_to_get_from_one_seed'], conf['total_articles_to_find_and_parse'], conf["base_urls"]


if __name__ == '__main__':
    max_num_articles, total_number, seed_urls = validate_config(CRAWLER_CONFIG_PATH)

    crawler = Crawler(seed_urls, total_number, max_num_articles, HEADERS)

    crawler.find_articles()

    prepare_environment(PROJECT_ROOT)

    for art_index, art_url in enumerate(crawler.urls, start=1):
        parser = ArticleParser(art_url, art_index)
        article = parser.parse()
        article.save_raw()
        sleep(random.randrange(1, 5))
