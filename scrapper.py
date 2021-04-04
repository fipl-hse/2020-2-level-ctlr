"""
Crawler implementation
"""

import json
import re
import os
import shutil

from random import randint
from time import sleep
import requests

from bs4 import BeautifulSoup
from constants import CRAWLER_CONFIG_PATH
from constants import ASSETS_PATH
from article import Article

headers = {'user-agent': "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/88.0.4324.190 Safari/537.36"}
    
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
    def __init__(self, seed_urls: list, total_max_articles: int, max_articles_per_seed: int):
        self.seed_urls = seed_urls
        self.total_max_articles = total_max_articles
        self.max_articles_per_seed = max_articles_per_seed
        self.urls = []

    @staticmethod
    def _extract_url(article_bs):
        news_container_id = 'MainMasterContentPlaceHolder_DefaultContentPlaceHolder_panelArticles'
        news_container = article_bs.find('div', attrs={'class': 'news-container', 'id': news_container_id})
        a_tags = news_container.find_all('a', id=re.compile('articleLink'))

        return [a_tag.attrs['href'] for a_tag in a_tags]

    def find_articles(self):
        for seed_url in self.seed_urls:
            response = requests.get(seed_url, headers=headers)
            page_soup = BeautifulSoup(response.content, 'lxml')
            extracted_urls = self._extract_url(page_soup)
            articles_to_add = self.total_max_articles - len(self.urls)
            if articles_to_add >= self.max_articles_per_seed:
                self.urls.extend(extracted_urls[:self.max_articles_per_seed])
            else:
                self.urls.extend(extracted_urls[:articles_to_add])
            if len(self.urls) < self.total_max_articles:
                sleep(randint(3, 6))
            else:
                break

    def get_search_urls(self):
        return self.urls


class ArticleParser:
    def __init__(self, article_url: str, article_id: int):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(article_url, article_id)

    def _fill_article_with_text(self, article_soup):
        text_list = list()
        annotation_tag = article_soup.find('p', id='MainMasterContentPlaceHolder_InsidePlaceHolder_articleAnnotation')
        text_list.append(annotation_tag.text)
        text_tag = article_soup.find('div', id='MainMasterContentPlaceHolder_InsidePlaceHolder_articleText')
        text_list.append(text_tag.text)
        self.article.text = '\n'.join(text_list)

    def _fill_article_with_meta_information(self, article_soup):
        title_tag = article_soup.find('a', id='MainMasterContentPlaceHolder_InsidePlaceHolder_articleHeader')
        self.article.title = title_tag.text
        author_tag = article_soup.find('a', id='MainMasterContentPlaceHolder_InsidePlaceHolder_authorName')
        self.article.author = author_tag.text
        topic_tags = article_soup.find_all('a', id=re.compile('[cC]ategoryName'))
        self.article.topics = [topic_tag.text for topic_tag in topic_tags]

    def unify_date_format(date_str):
        pass

    def parse(self):
        response = requests.get(self.article_url, headers=headers)
        article_bs = BeautifulSoup(response.content, 'lxml')
        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)

        return self.article


def prepare_environment(base_path):
    if os.path.exists(base_path):
        shutil.rmtree(os.path.dirname(base_path))
    os.makedirs(base_path)


def validate_config(crawler_path):
    with open(crawler_path) as json_file:
        config = json.load(json_file)

    urls = config['base_urls']
    total_artcls = config['total_articles_to_find_and_parse']
    max_artcls = config.get('max_number_articles_to_get_from_one_seed', total_artcls)

    if max_artcls > total_artcls:
        max_artcls = total_artcls

    is_url_ok = isinstance(urls, list) and all(isinstance(url, str) for url in urls)
    is_articles_num_ok = (isinstance(total_artcls, int) and not isinstance(total_artcls, bool) and
                          isinstance(max_artcls, int) and not isinstance(max_artcls, bool))

    if not is_url_ok:
        raise IncorrectURLError

    if not is_articles_num_ok:
        raise IncorrectNumberOfArticlesError

    is_articles_num_in_range = max_artcls != 0 and 1 <= total_artcls <= 1000

    if not is_articles_num_in_range:
        raise NumberOfArticlesOutOfRangeError

    if is_url_ok and is_articles_num_ok and is_articles_num_in_range:
        return urls, total_artcls, max_artcls

    raise UnknownConfigError


if __name__ == '__main__':
    # YOUR CODE HERE
    url_list, total, max_num = validate_config(CRAWLER_CONFIG_PATH)
    crawler = Crawler(seed_urls=url_list, total_max_articles=total, max_articles_per_seed=max_num)
    crawler.find_articles()
    prepare_environment(ASSETS_PATH)
    for i, full_url in enumerate(crawler.get_search_urls()):
        parser = ArticleParser(article_url=full_url, article_id=i+1)
        article = parser.parse()
        article.save_raw()
        sleep(randint(3, 6))
