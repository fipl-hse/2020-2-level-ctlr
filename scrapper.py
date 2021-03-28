"""
Crawler implementation
"""
from bs4 import BeautifulSoup
import requests
import time
from urllib.parse import urljoin, urldefrag
import json
import os
import shutil
import constants
from article import Article
from datetime import datetime
from mydate_framework import get_month

class LinkWorker:
    def __init__(self, page, relative_link):
        self.page = page
        self.relative_link = relative_link

    def get_absolute_link(self):
        result = urljoin(self.page, self.relative_link)
        return result

    def update_link(self, url):
        self.relative_link = url


class IncorrectURLError(Exception):
    """
    Custom error
    """
    pass


class NumberOfArticlesOutOfRangeError(Exception):
    """
    Custom error
    """
    pass


class IncorrectNumberOfArticlesError(Exception):
    """
    Custom error
    """
    pass


class UnknownConfigError(Exception):
    """
    Most general error
    """


lw = LinkWorker('', '')


class Crawler:
    """
    Crawler implementation
    """


    def __init__(self, seed_urls: list, max_articles: int, max_articles_per_seed: int):
        self.seed_urls = seed_urls
        self.max_articles = max_articles
        self.max_articles_per_seed = max_articles_per_seed
        self.urls = []

    @staticmethod  # ?
    def _extract_url(article_bs):
        global lw
        new_urls = []
        for a in article_bs.find_all('a'):
            link = str(a.get('href'))
            if link.find('html') == -1:
                continue
            if link.find('https://') == -1:
                try:
                    lw.update_link(link)
                    new_urls.append(lw.get_absolute_link())
                except:
                    pass
            else:
                try:
                    new_urls.append(link)
                except:
                    pass
        return new_urls

    def find_articles(self):
        """
        Finds articles
        """
        new_urls = []
        global lw
        lw = LinkWorker(self.seed_urls[0], "")
        for url in self.seed_urls:
            time.sleep(0.25)
            if len(self.urls) >= self.max_articles:
                break
            try:
                response = requests.get(url)
                parser = BeautifulSoup(response.text, 'lxml')
                m_urls = self._extract_url(parser)
                m_urls = m_urls[0:min(len(m_urls), self.max_articles_per_seed)]
                new_urls.extend(m_urls)
            except Exception:
                raise IncorrectURLError
        self.urls.extend(new_urls)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.urls


class ArticleParser:
    """
    ArticleParser implementation
    """

    def __init__(self, full_url: str, article_id: int):
        self.full_url = full_url
        self.article_id = article_id
        self.article = Article(self.full_url, self.article_id)

    def _fill_article_with_text(self, article_soup):
        try:
            self.article.text = article_soup.find(class_='content_cn').text.strip()
        except Exception as e:
            self.article.text = 'NOT FOUND'

    def _fill_article_with_meta_information(self, article_soup):
        date = article_soup.find(class_='claer public_data').find('span').text.strip()
        self.article.date = ArticleParser.unify_date_format(date)
        date_time_obj = datetime.strptime(self.article.date, '%Y-%m-%d %H:%M:%S')
        self.article.date = date_time_obj
        self.article.author = 'NOT FOUND'
        try:
            self.article.title = article_soup.find('h1').text
        except Exception:
            self.article.title = 'NOT FOUND'
        self.article.topics.append(self.article.title)

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format
        """
        try:
            arr = date_str.split(" ")
            arr[0] = arr[0][0:len(arr[0]) - 1]
            return arr[3] + '-' + get_month(arr[2]) + '-' + arr[1] + ' ' + arr[0] + ':00'
        except Exception:
            return "0000-00-00 00:00:00"

    def parse(self):
        """
        Parses each article
        """
        result = requests.get(self.full_url)
        soup_object = BeautifulSoup(result.text)
        self._fill_article_with_text(soup_object)
        self._fill_article_with_meta_information(soup_object)


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    path = os.path.join(base_path, 'tmp', 'articles')
    if os.path.exists(path):
        shutil.rmtree(path)  # remove recursively
    os.makedirs(path)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as read_file:
        json_dict = json.loads(read_file.read())
    if 'base_urls' not in json_dict:
        raise IncorrectURLError

    for url in json_dict['base_urls']:
        s = str(url)
        if s.find('http') == -1:
            raise IncorrectURLError('error')

    if not isinstance(json_dict["total_articles_to_find_and_parse"], int):
        raise IncorrectNumberOfArticlesError

    if json_dict["total_articles_to_find_and_parse"] <= 0 or json_dict["total_articles_to_find_and_parse"] > 100:
        raise NumberOfArticlesOutOfRangeError

    return json_dict['base_urls'], json_dict['total_articles_to_find_and_parse'], \
           json_dict['max_number_articles_to_get_from_one_seed']


if __name__ == '__main__':
    # YOUR CODE HERE
    prepare_environment(constants.PROJECT_ROOT)
    # crawler creation code
    urls, num_urls, max_seed_number = validate_config(constants.CRAWLER_CONFIG_PATH)
    crawler = Crawler(seed_urls=urls, max_articles=num_urls, max_articles_per_seed=max_seed_number)
    crawler.find_articles()
    id = 1
    for link in crawler.get_search_urls():
        article_parser = ArticleParser(link, id)
        id += 1
        article_parser.parse()
        article_parser.article.save_raw()
