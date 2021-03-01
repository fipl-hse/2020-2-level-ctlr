"""
Crawler implementation
"""

import json
from random import randint
import re
from time import sleep

from bs4 import BeautifulSoup
import requests

from constants import PROJECT_ROOT, ASSETS_PATH, CRAWLER_CONFIG_PATH


class IncorrectURLError(Exception):
    """
    Custom error
    """
    pass


class NumberOfArticlesOutOfRangeError(Exception):
    """
    Custom error
    """
    pass


class IncorrectNumberOfArticlesError(Exception):
    """
    Custom error
    """
    pass


class UnknownConfigError(Exception):
    pass


class BadStatusCode(Exception):
    pass


class Crawler:
    """
    Crawler implementation
    """
    def __init__(self, seed_urls: list, max_articles: int = None):
        self.seed_urls = seed_urls
        self.seed_urls_set = set()
        self.max_articles = max_articles
        self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                      '(KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'}
        self.article_urls = []

        for url in self.seed_urls:
            try:
                page = self.get_page(url)
            except BadStatusCode:
                continue
            else:
                soup = BeautifulSoup(page, 'html.parser')
                if len(self.article_urls) < self.max_articles:
                    self.find_articles(soup)
                self.get_search_urls(soup)
            self.seed_urls.pop(url)
        else:
            if len(self.article_urls) > max_articles:
                with open('links.txt', 'w') as f:
                    f.write('\n'.join(self.article_urls[:max_articles]))

    @staticmethod
    def _extract_url(article_bs):
        pass

    def find_articles(self, soup):
        """
        Finds articles
        """
        new_links = []
        for link in soup.find_all('a'):
            if res := re.findall(r'https://www.zvezdaaltaya.ru/\d{4}/\d{2}/.+', link.get('href')):
                if not re.findall(r'https://www.zvezdaaltaya.ru/\d{4}/\d{2}/\d{2}/', res[0]):
                    if res[0] not in self.article_urls:
                        new_links.append(res[0])
        with open('links.txt', 'a') as f:
            f.write('\n'.join(new_links) + '\n')
        self.article_urls.extend(new_links)

    def get_search_urls(self, soup):
        """
        Returns seed_urls param
        """
        for link in soup.find_all('a'):
            if res := re.findall(r'https://www.zvezdaaltaya.ru/.+', link.get('href')):
                if res[0] not in self.seed_urls:
                    self.seed_urls.append(res[0])
                    self.seed_urls_set.add(res[0])

    def get_page(self, url):
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            page = response.text
        else:
            raise BadStatusCode
        sleep(randint(3, 10))
        return page


class ArticleParser:
    """
    ArticleParser implementation
    """
    def __init__(self, full_url: str, article_id: int):
        self.full_url = full_url
        self.article_id = article_id

    def _fill_article_with_text(self, article_soup):
        self.text = ''
        for paragraph in article_soup.find_all('p')[:-3]:
            self.text += paragraph.text + ' '

    def _fill_article_with_meta_information(self, article_soup):
        self.title = re.sub(r' - Звезда Алтая', '', article_soup.find('title').text)
        self.date = article_soup.find('span', {'class' : 'mg-blog-date'}).text.strip()
        self.author = article_soup.find('h4', {'class': 'media-heading'}).find('a').text

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
    with open(crawler_path, 'r') as f:
        config = json.load(f)

    is_config_a_dict = isinstance(config, dict)
    is_base_urls_correct = (
            isinstance(config['base_urls'], list) and
            isinstance(config['base_urls'][0], str)
    )
    is_total_number_of_articles_correct = (
        isinstance(config['total_articles_to_find_and_parse'], int),
        config['total_articles_to_find_and_parse'] > 0
    )
    is_max_number_of_articles_int = (
        isinstance(config['max_number_articles_to_get_from_one_seed'], int),
        config['max_number_articles_to_get_from_one_seed'] > 0
    )

    is_max_number_of_articles_correct = (
            config['max_number_articles_to_get_from_one_seed'] <=
            config['total_articles_to_find_and_parse']
    )

    if all(
            is_config_a_dict,
            is_base_urls_correct,
            is_total_number_of_articles_correct,
            is_max_number_of_articles_int,
            is_max_number_of_articles_correct
    ):
        return config.values()

    elif not is_base_urls_correct:
        raise IncorrectURLError

    elif not is_total_number_of_articles_correct:
        raise IncorrectNumberOfArticlesError

    elif not is_max_number_of_articles_correct:
        raise NumberOfArticlesOutOfRangeError

    else:
        raise UnknownConfigError


if __name__ == '__main__':
    pass
    # try:
    #     seed_urls, max_articles, max_articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    # except (
    #         IncorrectURLError,
    #         IncorrectNumberOfArticlesError,
    #         NumberOfArticlesOutOfRangeError,
    #         UnknownConfigError
    # ):
    #     pass # todo script immediately finishes execution

