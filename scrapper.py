"""
Crawler implementation
"""
import random
import json
import datetime
import os
import re
from time import sleep
import requests
from requests.exceptions import MissingSchema
from bs4 import BeautifulSoup, NavigableString
from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH
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
        return article_bs.find('a').attrs['href']

    def find_articles(self):
        """
        Finds articles
        """
        self.get_search_urls()
        for seed_url in urls:
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

            urls_number = min(max_articles_num_per_seed, len(page_urls), (max_articles_num - len(self.urls)))
            for index in range(urls_number):
                self.urls.append('https://vn.ru' + self._extract_url(article_bs=page_urls[index]))

    def get_search_urls(self):
        """
        Returns seed_urls param
        """

        themes = ['ekonomika', 'oblast', 'obshchestvo',  'proisshestviya', 'dom', 'transport', 'razvlecheniya']
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

        article_text = article_soup.find('div', {'class': 'js-mediator-article divider-news clearfix'}).find_all('p')

        if not re.sub(r'[^А-Яа-я]', '', ''.join(list(map(lambda x: x.text, article_text)))):
            text = article_soup.find('div', {'class': 'js-mediator-article divider-news clearfix'}).contents
            text_list = []
            for item in text:
                if isinstance(item, NavigableString):
                    continue

                for index in range(len(item.contents)):
                    if isinstance(item.contents[index], NavigableString):
                        text_list.append(item.contents[index])
        else:
            text_list = list(map(lambda x: x.text, article_text))

        self.article.text = '\n'.join(text_list)

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find('h1').text

        self.article.author = article_soup.find('div', {'class': 'author-name floatleft clearfix'}).text.strip('\n')

        raw_topics = article_soup.find_all('div', {'class': 'on-footer-row'})
        self.article.topics = list(map(lambda x: x.find('a').text.lower(), raw_topics))

        raw_date = article_soup.find('div', {'class': 'nw-dn-date floatleft'}).text
        self.article.date = self.unify_date_format(raw_date)

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format
        """

        return datetime.datetime.strptime(date_str, '%d.%m.%Y')

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
        self._fill_article_with_meta_information(article_bs)
        self.article.save_raw()


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """

    try:
        os.makedirs(base_path, mode=0o777)
    except FileExistsError:
        for file in os.listdir(base_path):
            os.remove(f'{base_path}\\{file}')
    except OSError as error:
        raise error


def validate_config(crawler_path):
    """
    Validates given config
    """

    with open(crawler_path, 'r', encoding='utf-8') as file:
        config = json.load(file)

    if 'base_urls' not in config or not isinstance(config['base_urls'], list):
        raise IncorrectURLError

    try:
        for url in config['base_urls']:
            requests.get(str(url))
    except MissingSchema as error:
        raise IncorrectURLError from error

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

    urls, max_articles_num, max_articles_num_per_seed = validate_config(CRAWLER_CONFIG_PATH)

    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/88.0.4324.41 YaBrowser/21.2.0.1097 Yowser/2.5 Safari/537.36'}

    crawler = Crawler(seed_urls=urls,
                      max_articles=max_articles_num,
                      max_articles_per_seed=max_articles_num_per_seed)
    crawler.find_articles()

    prepare_environment(ASSETS_PATH)
    for i, url_full in enumerate(crawler.urls):
        parser = ArticleParser(full_url=url_full, article_id=i)
        parser.parse()
