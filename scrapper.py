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
from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH, PROJECT_ROOT

CRAWLER_SAVE_PATH = Path(PROJECT_ROOT) / 'intermediate_results.json'
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


class BadStatusCode(Exception):
    """
    Custom error
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
        links = []
        for tag in article_bs.find_all(class_='post-title'):
            links.append(tag.find('a').get('href'))
        return links

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
                    raise BadStatusCode
            except BadStatusCode:
                continue
            else:
                links = self._extract_url(soup_menu_page)
                links = list(set(links) - set(self.urls))
                if links:
                    limit = min(len(links), self.max_articles_per_seed)
                    for link in links[:limit]:
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


class CrawlerRecursive(Crawler):
    """
    Recursive Crawler
    """

    @staticmethod
    def _extract_url(article_bs):
        links = []
        if article_bs.find_all(class_='post-title'):
            for tag in article_bs.find_all(class_='post-title'):
                links.append(tag.find('a').get('href'))
        if article_bs.find(class_="crp_related"):
            for tag in article_bs.find(class_="crp_related").find_all('a'):
                links.append(tag.get('href'))
        return links

    def find_articles(self):
        """
        Finds articles
        """
        self._load_intermediate_results()
        seeds = self.get_search_urls()
        try:
            response = requests.get(seeds[0], headers=HEADERS)
            sleep(random.randrange(3, 6))
            if response.status_code == 200:
                soup_menu_page = BeautifulSoup(response.content, 'lxml')
            else:
                raise BadStatusCode
        except BadStatusCode:
            return self.find_articles()
        else:
            links = self._extract_url(soup_menu_page)
            links = list(set(links) - set(self.urls))
            if links:
                limit = min(len(links), self.max_articles_per_seed)
                for link in links[:limit]:
                    if len(self.urls) < self.total_max_articles:
                        self.urls.append(link)
                        self.seed_urls.append(link)
                self._save_intermediate_results()
                if len(self.urls) >= self.total_max_articles:
                    return self.urls[:self.total_max_articles]
        return self.find_articles()

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        current_seed = self.seed_urls[0]
        try:
            response = requests.get(current_seed, headers=HEADERS)
            sleep(random.randrange(2, 4))
            if response.status_code == 200:
                soup_page = BeautifulSoup(response.content, 'lxml')
            else:
                raise BadStatusCode
        except BadStatusCode:
            self.seed_urls.pop(0)
            return self.get_search_urls()
        else:
            if current_seed == 'https://astravolga.ru':
                for tag in soup_page.find(class_="dropdown").find_all('a'):
                    link = tag.get('href')
                    self.seed_urls.append(link)
            elif 'rubriki' in current_seed:
                for tag in soup_page.find_all('a', class_="page-numbers"):
                    link = tag.get('href')
                    self.seed_urls.append(link)
        return list(set(self.seed_urls))

    def _load_intermediate_results(self):
        if Path(CRAWLER_SAVE_PATH).exists():
            with open(CRAWLER_SAVE_PATH, 'r', encoding='utf-8') as file:
                dic = json.load(file)
            if self.seed_urls not in dic['seed_urls'] and not dic['seed_urls']:
                dic['seed_urls'].extend(self.seed_urls)
            self.seed_urls, self.urls = dic['seed_urls'], dic['article_urls']

    def _save_intermediate_results(self):
        with open(CRAWLER_SAVE_PATH, 'w', encoding='utf-8') as file:
            json.dump({"seed_urls": self.seed_urls[1:], "article_urls": self.urls}, file)


class ArticleParser:
    """
    ArticleParser implementation
    """
    def __init__(self, article_url: str, article_id: int):
        self.article_url = article_url
        self.article_id = article_id
        self.article = article.Article(article_url, article_id)

    def _fill_article_with_text(self, article_soup):
        text_soup = article_soup.find('div', class_="entry-content").find_all('p')
        text = '\n'.join([par.text.strip() for par in text_soup if par.text.strip()])
        if " " in text:
            text = text.replace(" ", ' ')
        self.article.text = text

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find('h1').text
        try:
            self.article.author = \
                article_soup.find('div', class_="title-post").find(rel='author').text
        except AttributeError:
            self.article.author = 'NOT FOUND'
        self.article.date = \
            self.unify_date_format(article_soup.find('div', class_="title-post").find('li').text)

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format
        """
        date = datetime.datetime.strptime(date_str, "%d.%m.%Y, %H:%M")
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
    if not isinstance(conf['total_articles_to_find_and_parse'], int)\
            or conf['total_articles_to_find_and_parse'] < 0:
        raise IncorrectNumberOfArticlesError
    if conf['total_articles_to_find_and_parse'] > 100:
        raise NumberOfArticlesOutOfRangeError
    return conf['base_urls'], conf['total_articles_to_find_and_parse'],\
        conf['max_number_articles_to_get_from_one_seed']


if __name__ == '__main__':
    # YOUR CODE HERE
    prepare_environment(ASSETS_PATH)
    urls, max_articles, articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    crawler = CrawlerRecursive(seed_urls=urls,
                               total_max_articles=max_articles,
                               max_articles_per_seed=articles_per_seed)
    articles = crawler.find_articles()
    for i, full_url in enumerate(crawler.urls, 1):
        parser = ArticleParser(article_url=full_url, article_id=i)
        article_from_list = parser.parse()
        article_from_list.save_raw()
        sleep(random.randrange(2, 5))
