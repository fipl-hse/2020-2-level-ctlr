"""
Crawler implementation
"""

import json
import os
from datetime import datetime
from random import randint
from time import sleep
import re
import shutil
import requests
from bs4 import BeautifulSoup
import article
from constants import CRAWLER_CONFIG_PATH, PROJECT_ROOT


class UnknownConfigError(Exception):
    """
    Most general error
    """


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


class IncorrectStatusCode(Exception):
    """"
    Custom error
    """


headers = {
        'user-agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'}


class Crawler:
    """
    Crawler implementation
    """

    def __init__(self, seed_urls: list, max_articles: int, max_articles_per_seed: int):
        self.seed_urls = seed_urls
        self.max_articles_per_seed = max_articles_per_seed
        self.max_articles = max_articles
        self.urls = []

    @staticmethod
    def _extract_url(article_bs):
        page_links = []
        for tag_a_content in article_bs.find_all('a'):
            get_url = tag_a_content.get('href')
            if get_url:
                re_url = re.findall(r'(/\w+/(\w+[-])+\w+\.html)', get_url)
                if re_url:
                    if get_url == re_url[0][0] and get_url not in page_links:
                        page_links.append('http://ks-yanao.ru' + get_url)
        return page_links

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            try:
                response = requests.get(seed_url, headers=headers)
                sleep(randint(2, 6))
                if response.status_code:
                    main_page_soup = BeautifulSoup(response.content, features='lxml')
                else:
                    raise IncorrectStatusCode
            except IncorrectStatusCode:
                continue
            else:
                found_links = self._extract_url(main_page_soup)
                if len(found_links) < self.max_articles_per_seed:
                    self.urls.extend(found_links)
                else:
                    self.urls.extend(found_links[:self.max_articles_per_seed])

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
        if os.path.exists(os.path.join(PROJECT_ROOT, 'saved_urls.json')):
            with open(os.path.join(PROJECT_ROOT, 'saved_urls.json'), encoding='utf-8') as file:
                saved_urls = json.load(file)
            if saved_urls['seed_urls']:
                self.seed_urls = saved_urls['seed_urls']
            if saved_urls['urls']:
                self.urls = saved_urls['urls']
            for seed_url in self.get_search_urls():
                try:
                    response = requests.get(seed_url, headers=headers)
                    sleep(randint(2, 6))
                    if response.status_code:
                        page_soup = BeautifulSoup(response.content, features='lxml')
                    else:
                        raise IncorrectStatusCode
                except IncorrectStatusCode:
                    continue
                else:
                    found_links = self._extract_url(page_soup)
                    new_links = [url for url in found_links if url not in self.urls]
                    if len(new_links) < self.max_articles_per_seed and len(self.urls) < self.max_articles:
                        self.urls.extend(new_links)
                    else:
                        self.urls.extend(new_links[:min(self.max_articles_per_seed, self.max_articles)])

                    saved_urls['seed_urls'].remove(seed_url)
                    saved_urls['urls'] = self.urls
                    with open(os.path.join(PROJECT_ROOT, 'saved_urls.json'), 'w', encoding='utf-8') as file:
                        json.dump(saved_urls, file)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        for seed_url in self.seed_urls:
            try:
                response = requests.get(seed_url, headers=headers)
                sleep(randint(2, 6))
                if response.status_code:
                    page_soup = BeautifulSoup(response.content, features='lxml')
                else:
                    raise IncorrectStatusCode
            except IncorrectStatusCode:
                continue
            else:
                if seed_url == 'http://ks-yanao.ru':
                    class_urls = page_soup.find('ul',
                                                class_='panel-menu-list list-unstyled text-uppercase').find_all('a')
                    for tag_a_content in class_urls:
                        found_link = tag_a_content.get('href')
                        if found_link not in self.seed_urls:
                            self.seed_urls.append(found_link)
                else:
                    found_links = self._extract_url(page_soup)
                    new_links = [link for link in found_links if link not in self.seed_urls]
                    self.seed_urls.extend(new_links)
        with open(os.path.join(PROJECT_ROOT, 'saved_urls.json'), encoding='utf-8') as file:
            saved_urls = json.load(file)
        saved_urls['seed_urls'] = self.seed_urls
        with open(os.path.join(PROJECT_ROOT, 'saved_urls.json'), 'w', encoding='utf-8') as file:
            json.dump(saved_urls, file)

        return self.seed_urls


class ArticleParser:
    """
    ArticleParser implementation
    """

    def __init__(self, full_url: str, article_id: int):
        self.full_url = full_url
        self.article_id = article_id
        self.article = article.Article(full_url, article_id)

    def _fill_article_with_text(self, article_soup):
        paragraphs_soup = article_soup.find('div', class_='element-detail').find_all('p')
        article_list = [paragraph.text.strip() for paragraph in paragraphs_soup if paragraph.text.strip()]
        article_str = ' '.join(article_list)
        self.article.text = article_str

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find('h1').text.strip()
        existed_author = article_soup.find('div', class_='text-box text-right').find('a').text.strip()
        if existed_author:
            self.article.author = existed_author
        else:
            self.article.author = 'NOT FOUND'
        self.article.date = self.unify_date_format(article_soup.find('p', class_='date font-open-s-light').text)

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format
        """
        date, time = date_str.split()
        day, month, year = date.split('.')
        hours, minutes, secs = time.split(':')
        date_int = tuple(map(int, [year, month, day, hours, minutes, secs]))
        valid_date = datetime(*date_int)
        return valid_date

    def parse(self):
        """
        Parses each article
        """
        response = requests.get(self.full_url, headers=headers)
        if response:
            article_soup = BeautifulSoup(response.content, features='lxml')
            self._fill_article_with_text(article_soup)
            self._fill_article_with_meta_information(article_soup)
        self.article.save_raw()

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
    with open(crawler_path) as opened_file:
        config = json.load(opened_file)

    is_config_unknown = ('base_urls' not in config
                         or 'total_articles_to_find_and_parse' not in config
                         or 'max_number_articles_to_get_from_one_seed' not in config)
    if not isinstance(config, dict) and is_config_unknown:
        raise UnknownConfigError

    are_urls_incorrect = (not isinstance(config['base_urls'], list)
                          or not all([isinstance(url, str) for url in config['base_urls']]))
    if are_urls_incorrect:
        raise IncorrectURLError

    is_num_articles_incorrect = (not isinstance(config['total_articles_to_find_and_parse'], int)
                                 #or not isinstance(config['max_number_articles_to_get_from_one_seed'], int)
                                 or config['total_articles_to_find_and_parse'] < 0
                                 #or config['max_number_articles_to_get_from_one_seed'] < 0
                                 )
    if is_num_articles_incorrect:
        raise IncorrectNumberOfArticlesError

    is_num_out_of_range = (config['total_articles_to_find_and_parse'] > 100)
    if is_num_out_of_range:
        raise NumberOfArticlesOutOfRangeError

    return config.values()


if __name__ == '__main__':
    # YOUR CODE HERE
    prepare_environment(PROJECT_ROOT)
    seed_urls_ex, max_articles_ex, max_articles_per_seed_ex = validate_config(CRAWLER_CONFIG_PATH)
    crawler = Crawler(seed_urls=seed_urls_ex,
                      max_articles=max_articles_ex,
                      max_articles_per_seed=max_articles_per_seed_ex)
    crawler.find_articles()
    for art_id, art_url in enumerate(crawler.urls, 1):
        parser = ArticleParser(full_url=art_url, article_id=art_id)
        article_from_list = parser.parse()
        sleep(randint(3, 5))
