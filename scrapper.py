"""
Crawler implementation
"""
import requests
from time import sleep
import random
import json
from constants import PROJECT_ROOT, ASSETS_PATH, CRAWLER_CONFIG_PATH
from bs4 import BeautifulSoup
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

    def __init__(self, seed_urls: list, max_articles: int, max_articles_per_seed: int):
        self.seed_urls = seed_urls
        self.max_articles = max_articles
        self.max_articles_per_seed = max_articles_per_seed
        self.urls = []

    @staticmethod
    def _extract_url(article_bs):
        pass

    def find_articles(self):
        """
        Finds articles
        """
        self.get_search_urls()
        for seed_url in seed_urls:
            try:
                response = requests.get(seed_url, headers=headers)
                sleep(random.randint(2, 6))
                response.encoding = 'utf-8'
                if not response:
                    raise IncorrectURLError

            except IncorrectURLError:
                continue

            page_content = response.content
            page_bs = BeautifulSoup(page_content, features='lxml')
            page_urls = page_bs.find_all('div', {'class': 'news-preview-content'})

            for i in range(min(max_articles, len(page_urls))):
                self.urls.append('https://vn.ru' + page_urls[i].contents[1].attrs['href'])

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        themes = ['oblast', 'obshchestvo', 'ekonomika', 'proisshestviya', 'dom', 'transport', 'razvlecheniya']
        self.seed_urls.extend([f'{self.seed_urls[0]}news/{theme}/' for theme in themes])


class ArticleParser:
    """
    ArticleParser implementation
    """

    def __init__(self, full_url: str, article_id: int):
        self.full_url = full_url
        self.article_id = article_id
        self.article = Article(full_url, article_id)

    def _fill_article_with_text(self, article_soup):
        pass

    def _fill_article_with_meta_information(self, article_soup):
        pass

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

        page_content = response.content
        article_bs = BeautifulSoup(page_content, features='lxml')
        self._fill_article_with_text(article_bs)


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    pass


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    if 'base_urls' not in config or not isinstance(config['base_urls'], list):
        raise IncorrectURLError
    else:
        try:
            for url in config['base_urls']:
                requests.get(str(url))
        except requests.exceptions.MissingSchema:
            raise IncorrectURLError

    if 'total_articles_to_find_and_parse' in config and \
            isinstance(config['total_articles_to_find_and_parse'], int) and \
            config['total_articles_to_find_and_parse'] not in range(0, 101):
        raise NumberOfArticlesOutOfRangeError

    if 'total_articles_to_find_and_parse' not in config or \
            not isinstance(config['total_articles_to_find_and_parse'], int) or \
            'max_number_articles_to_get_from_one_seed' not in config or \
            not isinstance(config['max_number_articles_to_get_from_one_seed'], int):
        raise IncorrectNumberOfArticlesError

    return config['base_urls'], \
           config['total_articles_to_find_and_parse'], \
           config['max_number_articles_to_get_from_one_seed']


if __name__ == '__main__':

    seed_urls, max_articles, max_articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)

    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/88.0.4324.41 YaBrowser/21.2.0.1097 Yowser/2.5 Safari/537.36'}

    crawler = Crawler(seed_urls=seed_urls,
                      max_articles=max_articles,
                      max_articles_per_seed=max_articles_per_seed)

    crawler.find_articles()

    for i, full_url in enumerate(crawler.urls):
        parser = ArticleParser(full_url=full_url, article_id=i)
        parser.parse()
