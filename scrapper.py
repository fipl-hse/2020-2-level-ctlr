"""
Crawler implementation
"""
import json
import os
from time import sleep
from datetime import datetime
import random
import shutil
import requests
from bs4 import BeautifulSoup
from article import Article
from constants import CRAWLER_CONFIG_PATH
from constants import PROJECT_ROOT


class IncorrectURLError(Exception):
    """
    Custom error
    """


class NumberOfArticlesOutOfRangeError(Exception):
    """
    Custom error
    """
class UnknownConfigError(Exception):
    """
    Most general error
    """

class IncorrectNumberOfArticlesError(Exception):
    """
    Custom error
    """
headers={
        'user-agent':
    'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/88.0.4324.152 YaBrowser/21.2.2.102 Yowser/2.5 Safari/537.36'}




class Crawler:
    """
    Crawler implementation
    """
    def __init__(self, seed_urls: list, max_articles: int,max_articles_per_seed:int):
        self.seed_urls = seed_urls
        self.total_max_articles = max_articles
        self.max_articles_per_seed = max_articles_per_seed
        self.urls = []

    @staticmethod
    def _extract_url(article_bs,max_articles_per_one_seed):
        links_page=[]
        for link in article_bs.find_all(class_='next news')[:max_articles_per_one_seed]:
            links_page.append(link.find('a').get('href'))
        return links_page

    def find_articles(self):
        """
        Finds articles
        """
        for url in self.seed_urls:
            sleep(random.randint(5,10))
            response=requests.get(url,headers=headers)
            if response.status_code==200:
                seed_soap=BeautifulSoup(response.content,features='lxml')
            self._extract_url(seed_soap,self.max_articles_per_seed)


    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.seed_urls


class ArticleParser:
    """
    ArticleParser implementation
    """
    def __init__(self, full_url: str, article_id: int):
        self.full_url = full_url
        self.article_id = article_id
        self.article = Article(self.full_url, self.article_id)


    def _fill_article_with_text(self, article_soup):
        text = article_soup.find('div',class_="announce").find_all("p")
        clean_text = [sent.text for sent in text]
        self.article.text = " ".join(clean_text)

    def _fill_article_with_meta_information(self, article_soup):
        title = article_soup.find('h4')
        self.article.title = title.text

        date = article_soup.find('p', class_="em")
        self.article.date = self.unify_date_format(date.text)

        self.article.author = 'NOT FOUND'

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format
        """
        unified_date = datetime.strptime(date_str.strip(), "%d.%m.%Y")
        return unified_date

    def parse(self):
        """
        Parses each article
        """
        response = requests.get(self.full_url, headers=headers)
        article_bs = BeautifulSoup(response.content, features='lxml')
        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)

        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """

    if os.path.exists(base_path):
        shutil.rmtree(base_path)
    os.makedirs(base_path)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path,'r', encoding='utf-8') as file:
        config = json.load(file)
    if not isinstance(config, dict) or not 'base_urls' in config \
            or not 'total_articles_to_find_and_parse' in config:
        raise UnknownConfigError
    if not isinstance(config['base_urls'], list) or not all(isinstance(url, str) for url in config['base_urls']):
        raise IncorrectURLError
    if not isinstance(config['total_articles_to_find_and_parse'], int):
        raise IncorrectNumberOfArticlesError
    if config['total_articles_to_find_and_parse'] > 100:
        raise NumberOfArticlesOutOfRangeError
    return config.values()


if __name__ == '__main__':
    # YOUR CODE HERE
    urls, max_articles_num, max_articles_num_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    crawler = Crawler(seed_urls=urls,
                      max_articles=max_articles_num,
                      max_articles_per_seed=max_articles_num_per_seed)
    articles = crawler.find_articles()
    prepare_environment(PROJECT_ROOT)
    for i, a_url in enumerate(crawler.urls):
        parser = ArticleParser(full_url=a_url, article_id=i + 1)
        parser.parse()
        parser.article.save_raw()
