"""
Crawler implementation
"""

import json
import re
import os
import shutil
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
        for url in self.seed_urls:
            response = requests.get(url, headers=headers)
            page_soup = BeautifulSoup(response.content, 'lxml')
            extracted_urls = self._extract_url(page_soup)
            articles_to_add = self.total_max_articles - len(self.urls)
            if articles_to_add >= self.max_articles_per_seed:
                self.urls.extend(extracted_urls[:self.max_articles_per_seed])
            else:
                self.urls.extend(extracted_urls[:articles_to_add])

    def get_search_urls(self):
        return self.urls


class ArticleParser:
    def __init__(self, article_url: str, article_id: int):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(article_url, article_id)

    def _fill_article_with_text(self, article_soup):
        list_of_texts = []
        annotation_tag = article_soup.find('p', id='MainMasterContentPlaceHolder_InsidePlaceHolder_articleAnnotation')
        list_of_texts += annotation_tag.text
        text_tag = article_soup.find('div', id='MainMasterContentPlaceHolder_InsidePlaceHolder_articleText')
        list_of_texts += text_tag.text
        self.article.text = '\n'.join(list_of_texts)

    def _fill_article_with_meta_information(self, article_soup):
        title = article_soup.find('a', id='MainMasterContentPlaceHolder_InsidePlaceHolder_articleHeader')
        self.article.title = title.text
        topics = article_soup.find_all('a', id=re.compile('[cC]ategoryName'))
        self.article.topics = [topic.text for topic in topics]
        author = article_soup.find('a', id='MainMasterContentPlaceHolder_InsidePlaceHolder_authorName')
        self.article.author = author.text

    def unify_date_format(date_str):
        pass

    def parse(self):
        response = requests.get(self.article_url, headers=headers)
        bs_article = BeautifulSoup(response.content, 'lxml')
        self._fill_article_with_text(bs_article)
        self._fill_article_with_meta_information(bs_article)
        return self.article


def prepare_environment(base_path):
    if os.path.exists(base_path):
        shutil.rmtree(base_path)
    os.makedirs(base_path)


def validate_config(crawler_path):
    with open(crawler_path, 'r', encoding='utf-8') as file:
        config = json.load(file)
    urls = config['base_urls']
    total_articles = config['total_articles_to_find_and_parse']
    max_articles = config.get('max_number_articles_to_get_from_one_seed', total_articles)
    url_checks = (isinstance(urls, list) and all(isinstance(url, str) for url in urls))
    articles_checks = (isinstance(total_articles, int) and not isinstance(total_articles, bool) and
                       isinstance(max_articles, int) and not isinstance(max_articles, bool))
    if not url_checks:
        raise IncorrectURLError
    if not articles_checks:
        raise IncorrectNumberOfArticlesError
    articles_num_in_range = (max_articles != 0 and 
                             1 <= total_articles <= 1000)
    if not articles_num_in_range:
        raise NumberOfArticlesOutOfRangeError
    if url_checks and articles_checks and articles_num_in_range:
        return urls, total_articles, max_articles
    raise UnknownConfigError


if __name__ == '__main__':
    # YOUR CODE HERE
    urls, total, max_num = validate_config(CRAWLER_CONFIG_PATH)
    crawler = Crawler(seed_urls=urls, total_max_articles=total, max_articles_per_seed=max_num)
    crawler.find_articles()
    prepare_environment(ASSETS_PATH)
    article_id = 0
    for full_url in crawler.get_search_urls():
        article_id += 1
        parser = ArticleParser(full_url, article_id)
        article = parser.parse()
        article.save_raw()
