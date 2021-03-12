"""
Crawler implementation
"""

from datetime import datetime
import json
import os
from random import randint
import re
from time import sleep

from bs4 import BeautifulSoup
import requests

from article import Article
import constants


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
    Custom error
    """


class BadStatusCode(Exception):
    """
    Custom error
    """


class BadArticle(Exception):
    """
    Custom Error
    """


class Crawler:
    """
    Crawler implementation
    """
    def __init__(self,
                 seed_urls: list,
                 max_articles: int = None,
                 max_articles_per_seed: int = None):
        self.seed_urls = seed_urls  # to parse
        self.max_articles = max_articles
        self.max_articles_per_seed = max_articles_per_seed
        self.seen_urls = set()
        self.urls = []  # articles urls

    @staticmethod
    def _extract_url(article_bs):
        article_urls = set(open(constants.ARTICLE_URLS, encoding='utf-8').read().split('\n'))
        seen_urls = set(open(constants.SEEN_URLS, encoding='utf-8').read().split('\n'))
        for link in article_bs.find_all('a'):
            if href := link.get('href'):
                if res := re.findall(r'https://www.zvezdaaltaya.ru/'
                                     r'\d{4}/\d{2}/.+/$', href):
                    if res[0] not in seen_urls:
                        article_urls.add(res[0])
        if article_urls:
            with open(constants.ARTICLE_URLS, 'w', encoding='utf-8') as file:
                file.write('\n'.join(article_urls) + '\n')
        return list(article_urls)  # todo

    def find_articles(self):
        """
        Finds articles
        """
        article_id = 1
        while self.seed_urls:
            seed_url = self.seed_urls.pop()
            try:
                self._process_page(seed_url)
            except BadStatusCode:
                continue
            else:
                if len(self.urls) > self.max_articles:
                    self.urls = self.urls[:self.max_articles]
                    break
                article_id += 1
                if article_id >= self.max_articles:
                    break

    def _process_page(self, url):
        """
        Processes page and get article urls
        """
        page = get_page(url)
        soup = BeautifulSoup(page, 'html.parser')
        self.urls = self._extract_url(soup, self.urls, self.seen_urls)
        return soup


class CrawlerRecursive(Crawler):
    """
    Recursive Crawler implementation
    """
    def __init__(self, seed_urls, max_articles, max_articles_per_seed):
        super().__init__(seed_urls, max_articles, max_articles_per_seed)
        self._load_previous_state()

    def find_articles(self):
        """
        Finds articles
        """
        article_id = 1
        while len(self.urls) < self.max_articles and self.seed_urls:
            seed_url = self.seed_urls.pop()
            try:
                soup = self._process_page(seed_url)
            except BadStatusCode:
                continue
            else:
                self.seed_urls = self.get_search_urls(soup)
                article_id += 1
        self.urls = self.urls[:self.max_articles]

    def get_search_urls(self, soup):
        """
        Returns seed_urls param
        """
        for idx, link in enumerate(soup.find_all('a')):
            if link.get('href'):
                if res := re.findall(r'https://www.zvezdaaltaya.ru/.+', link.get('href')):
                    if res[0] not in self.seen_urls:
                        self.seed_urls.append(res[0])
                        self.seen_urls.add(res[0])
            if idx % 10 == 0:
                with open(constants.TO_PARSE_URLS, 'w', encoding='utf-8') as file:
                    file.write('\n'.join(self.seed_urls))
                with open(constants.SEEN_URLS, 'w', encoding='utf-8') as file:
                    file.write('\n'.join(self.seen_urls))
        return self.seed_urls

    def _load_previous_state(self):
        if os.path.exists(constants.TO_PARSE_URLS):
            self.seed_urls = open(constants.TO_PARSE_URLS).read().split('\n')

        if os.path.exists(constants.SEEN_URLS):
            self.seen_urls = set(open(constants.SEEN_URLS).read().split('\n'))

        if os.path.exists(constants.ARTICLE_URLS):
            self.urls = open(constants.ARTICLE_URLS).read().split('\n')


class ArticleParser:
    """
    ArticleParser implementation
    """
    def __init__(self, full_url: str, article_id: int):
        self.full_url = full_url
        self.article_id = article_id
        self.article = Article(full_url, article_id)

    def _fill_article_with_text(self, article_soup):
        paragraphs = article_soup.find('div', {'class': 'mg-blog-post-box'})
        for paragraph in paragraphs.find_all('p'):
            self.article.text += paragraph.text + ' '

        if not self.article.text:
            raise BadArticle

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find('h1', {'class': 'title single'}).text.strip()
        date_str = article_soup.find('span', {'class': 'mg-blog-date'}).text.strip()
        self.article.date = self.unify_date_format(date_str)

        paragraphs = article_soup.find('div', {'class': 'mg-blog-post-box'})
        if res := paragraphs.find('p', {'class': 'has-text-align-right'}):
            self.article.author = res.text.title()
        elif len(paragraphs.find_all('p')[-1].text.split()) == 2:
            self.article.author = paragraphs.find_all('p')[-1].text.title()
        else:
            self.article.author = article_soup.find(
                'h4', {'class': 'media-heading'}).find('a').text.title()

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format
        """
        month_dict = {
            'Янв': 1,
            'Фев': 2,
            'Мар': 3,
            'Апр': 4,
            'Май': 5,
            'Июн': 6,
            'Июл': 7,
            'Авг': 8,
            'Сен': 9,
            'Окт': 10,
            'Ноя': 11,
            'Дек': 12
        }

        month, day, year = date_str.split()
        day = int(day[:-1])
        year = (int(year))
        month = month_dict[month]
        return datetime(year, month, day)

    def parse(self):
        """
        Parses each article
        """
        article_page = get_page(self.article.url)
        soup = BeautifulSoup(article_page, 'html.parser')
        self._fill_article_with_text(soup)
        self._fill_article_with_meta_information(soup)
        return self.article


def get_page(url):
    """
    Returns requests page
    """
    response = requests.get(url, headers=constants.HEADERS)
    response.encoding = 'utf-8'
    if response.status_code == 200:
        page = response.text
    else:
        raise BadStatusCode
    sleep(randint(3, 10))
    return page


def prepare_environment():
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if not os.path.exists(constants.ASSETS_PATH):
        os.makedirs(constants.ASSETS_PATH)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        config = json.load(file)

    is_config_a_dict = isinstance(config, dict)

    has_config_attributes = (
        'base_urls' in config and
        'total_articles_to_find_and_parse' in config
    )

    if not (is_config_a_dict and has_config_attributes):
        raise UnknownConfigError

    if 'max_number_articles_to_get_from_one_seed' not in config:
        config['max_number_articles_to_get_from_one_seed'] = \
            config['total_articles_to_find_and_parse']

    is_base_urls_correct = (
            isinstance(config['base_urls'], list) and
            all(re.match(r'https://www.zvezdaaltaya.ru/.*', url) for url in config['base_urls'])
    )

    if isinstance(config['total_articles_to_find_and_parse'], int):
        is_total_number_of_articles_correct = config['total_articles_to_find_and_parse'] > 0
    else:
        raise IncorrectNumberOfArticlesError

    is_max_number_of_articles_int = (
        isinstance(config['max_number_articles_to_get_from_one_seed'], int) and
        config['max_number_articles_to_get_from_one_seed'] > 0
    )

    is_max_number_of_articles_correct = (
            config['max_number_articles_to_get_from_one_seed'] <= 10000
    )

    if not is_base_urls_correct:
        raise IncorrectURLError

    if not is_total_number_of_articles_correct:
        raise IncorrectNumberOfArticlesError

    if not is_max_number_of_articles_correct:
        raise NumberOfArticlesOutOfRangeError

    if all((
            is_config_a_dict,
            has_config_attributes,
            is_base_urls_correct,
            is_total_number_of_articles_correct,
            is_max_number_of_articles_int,
            is_max_number_of_articles_correct
    )):
        return (config['base_urls'],
                config['total_articles_to_find_and_parse'],
                config['max_number_articles_to_get_from_one_seed'])

    raise UnknownConfigError


if __name__ == '__main__':
    prepare_environment()

    urls, articles_max, articles_per_seed = validate_config(constants.CRAWLER_CONFIG_PATH)
    crawler = CrawlerRecursive(
        seed_urls=urls,
        max_articles=articles_max,
        max_articles_per_seed=articles_per_seed
    )
    crawler.find_articles()

    articles_urls = open(constants.ARTICLE_URLS).read().split('\n')
    i = 1

    for article_url in articles_urls:
        print(f'Article #{i}: {article_url} is processed')
        parser = ArticleParser(full_url=article_url, article_id=i)
        try:
            article = parser.parse()
        except (BadStatusCode, BadArticle):
            continue
        else:
            article.save_raw()
            i += 1
        if i > articles_max:
            break
