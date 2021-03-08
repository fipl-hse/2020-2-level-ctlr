"""
Crawler implementation
"""
import requests
import json
import os
from bs4 import BeautifulSoup
from datetime import datetime
from constants import CRAWLER_CONFIG_PATH, ASSETS_PATH
from article import Article


HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/88.0.4324.41 YaBrowser/21.2.0.1099 Yowser/2.5 Safari/537.36 '
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
        url_article = article_bs.find('h2', class_="entry-title").find('a')
        return url_article.attrs['href']

    def find_articles(self):
        """
        Finds articles
        """
        for url in self.seed_urls:
            response = requests.get(url, headers=HEADERS)
            if not response:
                raise IncorrectURLError
            page_soup = BeautifulSoup(response.content, features='lxml')
            main_soup = page_soup.find('main', id='main')
            articles_soup = main_soup.find_all('article')
            for i in range(self.max_articles_per_seed):
                if len(self.urls) <= self.max_articles:
                    self.urls.append(self._extract_url(articles_soup[i]))

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        pass


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
        for p in article_texts:
            if 'class' not in p.attrs:
                self.article.text += p.text.strip() + ' '

    def _fill_article_with_meta_information(self, article_soup):
        # find title
        self.article.title = article_soup.find('h1', class_="entry-title").text

        # find topics
        for topic in article_soup.find_all('a', rel="category tag"):
            self.article.topics.append(topic.text)

        # find author
        self.article.author = article_soup.find('span', class_="author vcard").find('a').text

        # find date
        date_art = self.unify_date_format(article_soup.find('time', class_="entry-date published").text)
        self.article.date = date_art

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format: strftime("%Y-%m-%d %H:%M:%S")
        """
        date = '-'.join(date_str.split('.')[::-1])
        date_time = str(datetime.strptime(date, "%Y-%m-%d"))

        return datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")

    def parse(self):
        """
        Parses each article
        """
        response = requests.get(self.full_url, headers=HEADERS)
        if not response:
            raise IncorrectURLError

        article_soup = BeautifulSoup(response.content, features='lxml')
        self._fill_article_with_text(article_soup)
        self._fill_article_with_meta_information(article_soup)
        self.article.save_raw()


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if os.path.exists(base_path):
        for file in os.listdir(base_path):
            os.remove(base_path + file)
    else:
        try:
            os.makedirs(base_path, mode=0o777)
        except OSError as e:
            raise UnknownConfigError(e)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as file:
        crawler = json.load(file)

    if 'base_urls' not in crawler or not isinstance(crawler['base_urls'], list) or\
            not all([isinstance(url, str) for url in crawler['base_urls']]):
        raise IncorrectURLError

    if 'total_articles_to_find_and_parse' in crawler and \
            isinstance(crawler['total_articles_to_find_and_parse'], int) and \
            crawler['total_articles_to_find_and_parse'] > 40:
        raise NumberOfArticlesOutOfRangeError

    if 'max_number_articles_to_get_from_one_seed' not in crawler or\
            not isinstance(crawler['max_number_articles_to_get_from_one_seed'], int) or\
            'total_articles_to_find_and_parse' not in crawler or\
            not isinstance(crawler['total_articles_to_find_and_parse'], int):
        raise IncorrectNumberOfArticlesError

    seed_urls = crawler['base_urls']
    max_articles = crawler['total_articles_to_find_and_parse']
    max_articles_per_seed = crawler['max_number_articles_to_get_from_one_seed']
    return seed_urls, max_articles, max_articles_per_seed


if __name__ == '__main__':
    # YOUR CODE HERE
    seed_urls, max_articles, max_articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    crawler = Crawler(seed_urls=seed_urls, max_articles=max_articles, max_articles_per_seed=max_articles_per_seed)
    crawler.find_articles()

    prepare_environment(ASSETS_PATH)
    for ind, article_url in enumerate(crawler.urls):
        parser = ArticleParser(full_url=article_url, article_id=ind)
        parser.parse()
