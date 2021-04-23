"""
Crawler implementation
"""
import datetime
import json
from pathlib import Path
import random
import re
import shutil
from time import sleep

from bs4 import BeautifulSoup
import requests

import article
from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74'}


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
    def __init__(self, seed_urls: list, total_max_articles: int, max_articles_per_seed: int):
        self.seed_urls = seed_urls
        self.total_max_articles = total_max_articles
        self.max_articles_per_seed = max_articles_per_seed
        self.urls = []

    @staticmethod
    def _extract_url(article_bs):
        art_links = []
        for tag in article_bs.find_all(class_="el-title uk-h4"
                                              " uk-margin-top uk-margin-remove-bottom"):
            art_links.append('https://magadanpravda.ru/' + tag.find('a').get('href'))
        return art_links

    def find_articles(self):
        """
        Finds articles
        """
        for url in self.seed_urls:
            try:
                response = requests.get(url, headers=HEADERS)
                sleep(random.randrange(3, 6))
                if response.status_code == 200:
                    soup_menu_page = BeautifulSoup(response.content, 'lxml')
                else:
                    raise ConnectionError
            except ConnectionError:
                continue
            else:
                art_links = self._extract_url(soup_menu_page)
                art_links = list(set(art_links) - set(self.urls))
                if art_links:
                    limit = min(len(art_links), self.max_articles_per_seed)
                    for link in art_links[:limit]:
                        if len(self.urls) < self.total_max_articles:
                            self.urls.append(link)
                if len(self.urls) >= self.total_max_articles:
                    break
        return self.urls[:self.total_max_articles]

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.seed_urls


class ArticleParser:
    """
    ArticleParser implementation
    """
    def __init__(self, article_url: str, article_id: int):
        self.article_url = article_url
        self.article_id = article_id
        self.article = article.Article(article_url, article_id)

    def _fill_article_with_text(self, article_soup):
        text_soup = article_soup.find('div',
                                      class_="el-content uk-panel uk-margin-top").find_all('p')
        text = '\n'.join([par.text.strip() for par in text_soup if par.text.strip()])
        if " " in text:
            text = text.replace(" ", ' ')
        self.article.text = text

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find('h2').text.strip()
        self.article.author = 'NOT FOUND'
        self.article.date = \
            self.unify_date_format(article_soup.find('div',
                                                     class_="el-meta uk-text-meta"
                                                            " uk-margin-top").text)

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format
        """
        month_dict = {
            'января': '01',
            'февраля': '02',
            'марта': '03',
            'апреля': '04',
            'мая': '05',
            'июня': '06',
            'июля': '07',
            'августа': '08',
            'сентября': '09',
            'октября': '10',
            'ноября': '11',
            'декабря': '12'
        }
        date = date_str.split()
        date[1] = month_dict[date[1]]
        date = datetime.datetime.strptime(' '.join(date), "%d %m %Y | %H:%M")
        return date

    def parse(self):
        """
        Parses each article
        """
        response = requests.get(self.article_url, headers=HEADERS)
        if response:
            article_bs = BeautifulSoup(response.content, 'lxml')
            self._fill_article_with_text(article_bs)
            self._fill_article_with_meta_information(article_bs)
        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if Path(base_path).exists():
        shutil.rmtree(base_path)
    Path(base_path).mkdir(parents=True, exist_ok=True)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as file:
        conf = json.load(file)
    if not isinstance(conf, dict) and ('base_urls' not in conf
                                       or 'max_number_articles_to_get_from_one_seed' not in conf
                                       or 'total_articles_to_find_and_parse' not in conf):
        raise UnknownConfigError
    if not isinstance(conf['base_urls'], list):
        raise IncorrectURLError
    for url in conf['base_urls']:
        if not isinstance(url, str) or not re.findall(r'^https?://[0-9a-z]+.[0-9a-z]+[/_0-9a-z-]+', str(url)):
            raise IncorrectURLError
    if not isinstance(conf['total_articles_to_find_and_parse'], int) \
            or conf['total_articles_to_find_and_parse'] < 0:
        raise IncorrectNumberOfArticlesError
    if conf['total_articles_to_find_and_parse'] > 100:
        raise NumberOfArticlesOutOfRangeError
    return conf['base_urls'], conf['total_articles_to_find_and_parse'], \
        conf['max_number_articles_to_get_from_one_seed']


if __name__ == '__main__':
    # YOUR CODE HERE
    prepare_environment(ASSETS_PATH)
    urls, max_articles, articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    crawler = Crawler(seed_urls=urls,
                      total_max_articles=max_articles,
                      max_articles_per_seed=articles_per_seed)
    articles = crawler.find_articles()
    for i, full_url in enumerate(articles):
        parser = ArticleParser(article_url=full_url, article_id=i)
        article_from_list = parser.parse()
        article_from_list.save_raw()
        sleep(random.randrange(2, 5))
