"""
Crawler implementation
"""
import requests
import json
from bs4 import BeautifulSoup
from time import sleep
import random
from article import Article
import os

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
        url = article_bs.contents[1]
        return url.get('href')

    def find_articles(self):
        """
        Finds articles
        """
        for url in self.seed_urls:
            response = requests.get(url, headers=headers)
            if not response:
                raise IncorrectURLError
            if response.status_code == 200:
                sleep(random.randrange(2, 6))
            page_soup = BeautifulSoup(response.content, features='lxml')
            article_soup = page_soup.find_all('div', class_='article-info')
            for article_bs in article_soup[:self.max_articles_per_seed]:
                self.urls.append(self._extract_url(article_bs))
                if len(self.urls) == self.max_articles:
                    break
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
        self.article = Article(self.full_url, self.article_id)

    def _fill_article_with_text(self, article_soup):
        text_soup = article_soup.find_all('p')
        text = ''
        for element in text_soup[:-4]:
            text += element.text
        return text.strip()

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find('h1').text.strip()
        return None

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
        response = requests.get(self.full_url, headers=headers)
        if not response:
            raise IncorrectURLError
        article_soup = BeautifulSoup(response.content, features='lxml')
        self.article.text += self._fill_article_with_text(article_soup)
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
    with open(crawler_path, 'r') as crawler_config_file:
        config = json.load(crawler_config_file)

    urls = config['base_urls']
    total_articles = config['total_articles_to_find_and_parse']
    max_articles = config.get('max_number_articles_to_get_fom_one_seed', total_articles)

    if not isinstance(config, dict):
        raise UnknownConfigError

    if not isinstance(urls, list) and not all(isinstance(url, str) for url in urls):
        raise IncorrectURLError

    if not isinstance(total_articles, int) and isinstance(total_articles, bool) and \
            not isinstance(max_articles, int) and isinstance(max_articles, bool):
        raise IncorrectNumberOfArticlesError

    articles_num_in_range = 0 < max_articles <= total_articles and 5 <= total_articles <= 10000

    if not articles_num_in_range:
        raise NumberOfArticlesOutOfRangeError

    else:
        return urls, total_articles, max_articles


if __name__ == '__main__':
    # YOUR CODE HERE
    from constants import CRAWLER_CONFIG_PATH
    from constants import ASSETS_PATH

    urls_list, total_art, max_number = validate_config(CRAWLER_CONFIG_PATH)
    crawler = Crawler(seed_urls=urls_list, max_articles=total_art, max_articles_per_seed=max_number)
    article_urls = crawler.find_articles()
    prepare_environment(ASSETS_PATH)
    article_id = 0
    for article_url in article_urls:
        article_id += 1
        parser = ArticleParser(article_url, article_id)
        sleep(random.randint(3, 6))
        article = parser.parse()
        article.save_raw()