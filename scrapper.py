"""
Crawler implementation
"""
import json
import os
import shutil
from random import randint
from time import sleep
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import article
from constants import CRAWLER_CONFIG_PATH, ASSETS_PATH


headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/88.0.4324.190 Safari/537.36'
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
    def __init__(self, seed_urls: list, max_articles: int, max_article_per_seed: int):
        self.seed_urls = seed_urls
        self.max_articles = max_articles
        self.max_articles_per_seed = max_article_per_seed
        self.urls = []

    @staticmethod
    def _extract_url(article_bs):
        article_links = [tag.find('a').get('href') for tag in article_bs.find_all(class_='thumb')]
        return article_links

    def find_articles(self):
        """
        Finds articles
        """
        for url in self.seed_urls:
            response = requests.get(url, headers=headers)
            sleep(randint(2, 5))

            if response.status_code == 200:
                seed_url_soup = BeautifulSoup(response.content, 'lxml')

                links = self._extract_url(seed_url_soup)
                if links:
                    links = links[:self.max_articles_per_seed] if len(links) > self.max_articles_per_seed else links
                    for link in links:
                        if len(self.urls) < self.max_articles:
                            self.urls.append(link)

            if self.urls == self.max_articles:
                break

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
        self.article = article.Article(url=full_url, article_id=article_id)

    def _fill_article_with_text(self, article_soup):
        article_text = article_soup.find('div', class_="entry-post").find_all('p')
        article_list = [paragraph.text.strip() for paragraph in article_text]
        self.article.text = '\n'.join(article_list)

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find('div', class_="head-post").find('h2').text.strip()

        try:
            self.article.author = article_soup.find('div', class_="author").find('a').text.strip()
        except AttributeError:
            self.article.author = 'NOT FOUND'

        raw_date = article_soup.find('span', class_="time")['title']
        self.article.date = self.unify_date_format(raw_date)

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format
        """
        unified_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S") # need to check
        return unified_date

    def parse(self):
        """
        Parses each article
        """
        response = requests.get(url=self.full_url, headers=headers)
        if response.status_code == 200:
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
    with open(crawler_path, 'r', encoding='utf-8') as file:
        crawler_config = json.load(file)

    if not isinstance(crawler_config['base_urls'], list):
        raise IncorrectURLError

    for url in crawler_config['base_urls']:
        if not isinstance(url, str):
            raise IncorrectURLError

    if (not isinstance(crawler_config['total_articles_to_find_and_parse'], int) or
            isinstance(crawler_config['total_articles_to_find_and_parse'], bool)):
        raise IncorrectNumberOfArticlesError

    if (not isinstance(crawler_config['max_number_articles_to_get_from_one_seed'], int) or
            isinstance(crawler_config['max_number_articles_to_get_from_one_seed'], bool)):
        raise IncorrectNumberOfArticlesError

    if (crawler_config['total_articles_to_find_and_parse'] > 100 or
            crawler_config['total_articles_to_find_and_parse'] <= 0):
        raise NumberOfArticlesOutOfRangeError

    if (crawler_config['max_number_articles_to_get_from_one_seed'] > 100 or
            crawler_config['max_number_articles_to_get_from_one_seed'] <= 0):
        raise NumberOfArticlesOutOfRangeError

    urls = crawler_config['base_urls']
    max_articles = crawler_config['total_articles_to_find_and_parse']
    max_articles_per_seed = crawler_config['max_number_articles_to_get_from_one_seed']

    return urls, max_articles, max_articles_per_seed

if __name__ == '__main__':
    prepare_environment(ASSETS_PATH)

    needed_urls, max_articles_num, max_articles_per_seed_num = validate_config(CRAWLER_CONFIG_PATH)

    crawler = Crawler(seed_urls=needed_urls,
                      max_articles=max_articles_num,
                      max_articles_per_seed=max_articles_per_seed_num)

    crawler.find_articles()

    for url_id, url_full in enumerate(crawler.urls):
        parser = ArticleParser(full_url=url_full, article_id=url_id + 1)
        parsed_article = parser.parse()
        parsed_article.save_raw()
        sleep(randint(2, 6))
