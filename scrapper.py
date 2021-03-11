"""
Crawler implementation
"""
import json
import os
import requests

from datetime import datetime
from bs4 import BeautifulSoup
from article import Article
from constants import CRAWLER_CONFIG_PATH
from constants import HEADERS
from urllib.parse import urlparse


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
        self.total_max_articles = max_articles
        self.max_articles_per_seed = max_articles_per_seed

        self.urls = []

    @staticmethod
    def _extract_url(article_bs):
        articles = article_bs.find_all('div', {'itemprop': 'blogPost'})
        current_seed_links = []
        for blog_tag in articles:
            article_name_tag = blog_tag.find('h2', {'itemprop': 'name'})
            article_link = article_name_tag.a
            current_seed_links.append(article_link.attrs['href'])
        return current_seed_links

    def find_articles(self):
        """
        Finds articles
        """
        for url in self.seed_urls:
            url_parsed = urlparse(url)
            url_scheme, url_domain = url_parsed.scheme, url_parsed.netloc
            url_base = '{}://{}'.format(url_scheme, url_domain)

            # Change user-agent to avoid 403 error
            response = requests.get(url, headers=HEADERS)  # make a request to seed url
            if response:
                content = response.text
                links = self._extract_url(BeautifulSoup(content, 'html.parser'))
                full_links = []

                for link in links:
                    if link.startswith('/'):
                        full_links.append(url_base + link)
                    else:
                        full_links.append(link)

                self.urls.extend(full_links[:max_articles_per_seed])
        assert len(self.urls) >= self.total_max_articles

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
        self.article.text = article_soup.find("div", class_="leading-0").text

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find('div', class_="page-header").text.strip()
        self.article.views = article_soup.find('div', class_="hits").find('meta').text
        self.article.date = self.unify_date_format(article_soup.find('div', class_="create").find('time').text)
        self.article.author = 'NOT FOUND'

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format
        """
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

    def parse(self):
        """
        Parses each article
        """
        response = requests.get(self.full_url, headers=HEADERS)
        article_soup = BeautifulSoup(response.content, features='lxml')
        self._fill_article_with_text(article_soup)
        self._fill_article_with_meta_information(article_soup)
        self.article.save_raw()


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if not os.path.isdir(base_path):
        os.makedirs(base_path)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as config:
        params = json.load(config)

    if 'base_urls' not in params or not all([isinstance(url, str) for url in params['base_urls']]):
        raise IncorrectURLError

    if params['total_articles_to_find_and_parse'] > 100:
        raise NumberOfArticlesOutOfRangeError

    if not isinstance(params['total_articles_to_find_and_parse'], int):
        raise IncorrectNumberOfArticlesError

    return params['base_urls'], params['total_articles_to_find_and_parse'], params['total_articles_to_find_and_parse']


if __name__ == '__main__':
    #YOUR CODE HERE
    try:
        seed_urls, max_articles, max_articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)
        crawler = Crawler(seed_urls=seed_urls,
                          max_articles=max_articles,
                          max_articles_per_seed=max_articles_per_seed)
        crawler.find_articles()

        for i, url in enumerate(crawler.urls):
            parser = ArticleParser(full_url=url, article_id=i)
    except (IncorrectURLError, IncorrectNumberOfArticlesError, NumberOfArticlesOutOfRangeError, UnknownConfigError):
        exit(1)
