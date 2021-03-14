"""
Crawler implementation
"""
import requests
import json
from time import sleep
import random
from bs4 import BeautifulSoup
import os
from article import Article
from constants import CRAWLER_CONFIG_PATH
from constants import ASSETS_PATH
headers = {
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 YaBrowser/21.2.2.102 Yowser/2.5 Safari/537.36'
        }
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
        url_article = article_bs.find('div', class_='entry-title').find('a')
        link = url_article.attrs['href']
        return 'https://севернаяправда.рф/' + link

    def find_articles(self):
        """
        Finds articles
        """
        for urls in self.seed_urls:
            response = requests.get(urls, headers=headers)
            sleep(random.randrange(3, 6))
            if not response:
                raise IncorrectURLError
            soup = BeautifulSoup(response.content, features='lxml')
            links = self._extract_url(soup)
            if len(links) < self.max_articles_per_seed:
                self.urls.extend(links)
            else:
                self.urls.extend(links[:self.max_articles_per_seed])


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
        self.article = Article(full_url, article_id)


    def _fill_article_with_text(self, article_soup):
        article_texts = article_soup.find_all('p')
        filling_article = []
        for texts in article_texts:
            if 'class' not in texts.attrs:
                filling_article.append(texts.text.strip())
        self.article.text = ' '.join(filling_article)


    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find('h1', class_="entry-title").text
        self.article.author = 'NOT FOUND'
        for topic in article_soup.find_all('a', rel="tag"):
            self.article.topics.append(topic.text)
        date = article_soup.find('span', class_='submitted').text.split()
        self.article.date = date[1]


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
        response = requests.get(self.full_url, headers=headers)
        if not response:
            raise IncorrectURLError
        article_soup = BeautifulSoup(response.content, features='lxml')
        self._fill_article_with_text(article_soup)
        self._fill_article_with_meta_information(article_soup)
        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if not os.path.exists(base_path):
        os.makedirs(base_path)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as file:
        configuration = json.load(file)
    if not isinstance(configuration, dict):
        raise UnknownConfigError
    if not isinstance(configuration['base_urls'], list) or \
            not all(isinstance(url, str) for url in configuration['base_urls']):
        raise IncorrectURLError
    if 'total_articles_to_find_and_parse' in configuration and \
            isinstance(configuration['total_articles_to_find_and_parse'], int) and \
            configuration['total_articles_to_find_and_parse'] > 100:
        raise NumberOfArticlesOutOfRangeError
    if 'max_number_articles_to_get_from_one_seed' not in configuration or \
            not isinstance(configuration['max_number_articles_to_get_from_one_seed'], int) or \
            'total_articles_to_find_and_parse' not in configuration or \
            not isinstance(configuration['total_articles_to_find_and_parse'], int):
        raise IncorrectNumberOfArticlesError

    return configuration.values()






if __name__ == '__main__':
    urls, max_num_articles, max_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    crawler_current = Crawler(seed_urls=urls, max_articles=max_num_articles, max_articles_per_seed=max_per_seed)
    crawler_current.find_articles()
    prepare_environment(ASSETS_PATH)
    for ind, article_url in enumerate(crawler_current.urls):
        parser = ArticleParser(full_url=article_url, article_id=ind + 1)
        parser.parse()
