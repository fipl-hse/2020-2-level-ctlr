"""
Crawler implementation
"""
import json
import os
from time import sleep
import datetime
import random
import shutil
import requests
from bs4 import BeautifulSoup
import article
from constants import CRAWLER_CONFIG_PATH, PROJECT_ROOT

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
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
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    sleep(random.randrange(3, 6))
                    soup_menu_page = BeautifulSoup(response.content, 'lxml')
                else:
                    raise BadStatusCode
            except BadStatusCode:
                continue
            else:
                links = self._extract_url(soup_menu_page)
                links = [link for link in links if link not in self.urls]
                if links:
                    limit = min(len(links), self.max_articles_per_seed)
                    for link in links[:limit]:
                        if len(self.urls) < self.total_max_articles:
                            self.urls.append(link)
                if len(self.urls) == self.total_max_articles:
                    break
        return self.urls

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.seed_urls


class CrawlerRecursive(Crawler):
    """
    Recursive Crawler
    """

    def find_articles(self):
        """
        Finds articles
        """
        if os.path.exists(os.path.join(PROJECT_ROOT, 'intermediate_results.json')):
            with open(os.path.join(PROJECT_ROOT, 'intermediate_results.json'),
                      'r', encoding='utf-8') as file:
                results = json.load(file)
            if results['seed_urls']:
                self.seed_urls = results['seed_urls']
            if results['article_urls']:
                self.urls = results['article_urls']
        for url in self.get_search_urls():
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    sleep(random.randrange(3, 6))
                    soup_menu_page = BeautifulSoup(response.content, 'lxml')
                else:
                    raise BadStatusCode
            except BadStatusCode:
                continue
            else:
                links = self._extract_url(soup_menu_page)
                links = [link for link in links if link not in self.urls]
                if links:
                    limit = min(len(links), self.max_articles_per_seed)
                    for link in links[:limit]:
                        if len(self.urls) < self.total_max_articles:
                            self.urls.append(link)
                    with open(os.path.join(PROJECT_ROOT, 'intermediate_results.json'),
                              'r', encoding='utf-8') as file:
                        results = json.load(file)
                    results['seed_urls'].remove(url)
                    results['article_urls'] = self.urls
                    with open(os.path.join(PROJECT_ROOT, 'intermediate_results.json'), 'w', encoding='utf-8') as file:
                        json.dump(results, file)
                if len(self.urls) == self.total_max_articles:
                    break
        return self.urls

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        for link in self.seed_urls:
            try:
                if len(self.seed_urls) > 100:
                    with open(os.path.join(PROJECT_ROOT, 'intermediate_results.json'),
                              'r', encoding='utf-8') as file:
                        results = json.load(file)
                    results['seed_urls'] = self.seed_urls
                    with open(os.path.join(PROJECT_ROOT, 'intermediate_results.json'), 'w',
                              encoding='utf-8') as file:
                        json.dump(results, file)
                    break
                response = requests.get(link, headers=headers)
                if response.status_code == 200:
                    sleep(random.randrange(1, 2))
                    soup_page = BeautifulSoup(response.content, 'lxml')
                else:
                    raise BadStatusCode
            except BadStatusCode:
                continue
            else:
                if link == 'https://astravolga.ru' and len(self.seed_urls) == 1:
                    for tag in soup_page.find_all(class_='menu-item menu-item-type-taxonomy'
                                                         ' menu-item-object-category'
                                                         ' menu-item-87549'):
                        link = tag.find('a').get('href')
                        if link not in self.seed_urls:
                            self.seed_urls.append(link)
                else:
                    for tag in soup_page.find_all('a', class_="page-numbers"):
                        link = tag.get('href')
                        if link not in self.seed_urls:
                            self.seed_urls.append(link)
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
        response = requests.get(self.article_url, headers=headers)
        if response:
            article_bs = BeautifulSoup(response.content, 'lxml')
            self._fill_article_with_text(article_bs)
            self._fill_article_with_meta_information(article_bs)
        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if os.path.exists(os.path.join(base_path, 'tmp', 'articles')):
        shutil.rmtree(os.path.join(base_path, 'tmp', 'articles'))
    os.makedirs(os.path.join(base_path, 'tmp', 'articles'))


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
    if not isinstance(conf['base_urls'], list) or \
            not all([isinstance(seed_url, str) for seed_url in conf['base_urls']]):
        raise IncorrectURLError
    if not isinstance(conf['total_articles_to_find_and_parse'], int)\
            or conf['total_articles_to_find_and_parse'] < 0:
        raise IncorrectNumberOfArticlesError
    if conf['total_articles_to_find_and_parse'] > 100:
        raise NumberOfArticlesOutOfRangeError
    return conf.values()


if __name__ == '__main__':
    # YOUR CODE HERE
    prepare_environment(PROJECT_ROOT)
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
