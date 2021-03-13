"""
Crawler implementation
"""
import json
import os
from time import sleep
import random
import re
import requests
from bs4 import BeautifulSoup
from article import Article
from constants import CRAWLER_CONFIG_PATH
from constants import ASSETS_PATH

headers = {
            'user-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36'
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
        return article_bs.findAll('a', attrs={'href': re.compile("/node/")})

    def find_articles(self):
        """
        Finds articles
        """

        for url in self.seed_urls:
            response = requests.get(url, headers=headers)
            sleep(random.randrange(3,5))
            page = BeautifulSoup(response.content, features='lxml')
            links = self._extract_url(page)
            for link in links:
                link2 = re.findall(r'/node/\d{4}', str(links))

            for link_url in link2:
                code = 'http://kamtime.ru' + link_url
                if code not in self.urls and len(self.urls) < self.max_articles:
                    self.urls.append(code)

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
        self.article = Article(url=full_url, article_id=article_id)

    def _fill_article_with_text(self, article_soup):
        self.article.text = article_soup.find('div', class_="content clear-block").text.strip()
        print(self.article.text)


    def _fill_article_with_meta_information(self, article_soup):
        pass

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format
        """
        pass

    def parse(self):
        response = requests.get(self.full_url, headers=headers)

        article_bs = BeautifulSoup(response.content, features='lxml')

        self._fill_article_with_text(article_bs)
        #self.article.save_raw()



def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if not os.path.exists(base_path):
        os.makedirs(base_path)


def validate_config(crawler_path):
    with open(crawler_path, 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)

    if not isinstance(config, dict):
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
    seed_urls, max_articles, max_articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)
    crawler = Crawler(seed_urls, max_articles, max_articles_per_seed)
    article = crawler.find_articles()
    print(article)


    prepare_environment(ASSETS_PATH)
    for ind, url in enumerate(article):
        parser = ArticleParser(url, ind)
        articles = parser.parse()


