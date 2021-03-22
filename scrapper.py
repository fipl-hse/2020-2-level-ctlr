"""
Crawler implementation
"""
from bs4 import BeautifulSoup
import constants
from time import sleep
import json
import requests
from article import Article
import os
from datetime import datetime
import shutil

from tls_adapter import TLSAdapter


headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)' 
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
    def __init__(self, seed_urls: list, max_articles: int, max_articles_per_seed:int):
        self.seed_urls = seed_urls
        self.max_articles = max_articles
        self.max_articles_per_seed = max_articles_per_seed
        self.urls = []

    @staticmethod
    def _extract_url(article_bs):
        return article_bs.find('div', class_="articles-list-item").find('a').attrs['href']

    def find_articles(self):
        """
        Finds articles
        """
        for url in self.seed_urls:
            response = session.get(url, headers=headers)
            sleep(5)
            print('Requesting')

            soup_page = BeautifulSoup(response.content, features='lxml')
            all_urls_soup = soup_page.find_all('div', class_="articles-list-block")
            for one_of_urls in all_urls_soup[:max_articles_per_seed]:
                if len(self.urls) < self.max_articles:
                    self.urls.append('https://www.ks87.ru'+self._extract_url(one_of_urls))

            if len(self.urls) == self.max_articles:
                return self.urls


    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        pass


class ArticleParser:
    """
    ArticleParser implementation
    """
    def __init__(self, full_url: str, article_id: int):
        self.full_url = full_url
        self.article_id = article_id
        self.article = Article(self.full_url, self.article_id)

    def _fill_article_with_text(self, article_soup):
        articles_info = article_soup.find('div', class_="content-block").find('div').text
        article_text = ''
        for article in articles_info:
            article_text += str(article)
            return article_text.strip()

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find('div', class_='articles-body').find('h1').text
        self.article.author = article_soup.find('strong').text
        self.article.date = self.unify_date_format(article_soup.find('div', class_='articles-body-date').text[2:-3].strip())
        return None

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format
        """
        return datetime.strptime(date_str, "%d.%m.%Y")

    def parse(self):
        """
        Parses each article
        """
        response = session.get(self.full_url, headers=headers)
        sleep(5)
        print('Requesting')
        article_soup = BeautifulSoup(response.content, features='lxml')
        self._fill_article_with_text(article_soup)
        self._fill_article_with_meta_information(article_soup)
        return self.article.save_raw()


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    shutil.rmtree(base_path, ignore_errors=True)
    if not os.path.isdir(base_path):
        os.makedirs(base_path)

def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as file:
        crawler_config = json.load(file)

    for base_url in crawler_config["base_urls"]:
        if base_url[:8] != 'https://' and not base_url.startswith('http://)':
            raise IncorrectURLError

    if not isinstance(crawler_config['total_articles_to_find_and_parse'], int):
        raise IncorrectNumberOfArticlesError

    if ("total_articles_to_find_and_parse" in crawler_config
        and crawler_config["total_articles_to_find_and_parse"] > 100) \
            or not isinstance(crawler_config['max_number_articles_to_get_from_one_seed'], int):
        raise NumberOfArticlesOutOfRangeError

    return crawler_config['base_urls'], crawler_config['total_articles_to_find_and_parse'], \
           crawler_config['max_number_articles_to_get_from_one_seed']

if __name__ == '__main__':
    # YOUR CODE HERE
    session = requests.session()
    session.mount('https://', TLSAdapter())

    seed_urls, max_articles, max_articles_per_seed = validate_config(constants.CRAWLER_CONFIG_PATH)
    crawler = Crawler(seed_urls, max_articles, max_articles_per_seed)
    crawler.find_articles()
    prepare_environment(constants.ASSETS_PATH)

    for i, article_url in enumerate(crawler.urls):
        parser = ArticleParser(full_url=article_url, article_id=i)
        parser.parse()
        parser.article.save_raw()
