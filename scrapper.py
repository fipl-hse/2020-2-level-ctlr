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
from mydate_worker import get_month


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


LW = LinkWorker('', '')


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
        global LW
        new_urls = []
        for a_element in article_bs.find_all('a'):
            my_link = str(a_element.get('href'))
            if my_link.find('news/') == -1 or my_link.find('HEADING') != -1 or my_link == '/news/':
                continue
            if my_link.find('https://') == -1:
                try:
                    LW.update_link(my_link)
                    new_urls.append(LW.get_absolute_link())
                except AttributeError:
                    pass
            else:
                try:
                    new_urls.append(my_link)
                except AttributeError:
                    pass
        return new_urls

    def find_articles(self):
        """
        Finds articles
        """
        new_urls = []
        global LW
        LW = LinkWorker(self.seed_urls[0], "")
        for url in self.seed_urls:
            time.sleep(0.25)
            if self.max_articles != 0 and len(self.urls) >= self.max_articles:
                break
            try:
                response = requests.get(url)
                parser = BeautifulSoup(response.text, 'lxml')
                m_urls = self._extract_url(parser)
                if self.max_articles_per_seed != 0:
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

    def __init__(self, full_url: str, article_id: int, save_path=''):
        self.full_url = full_url
        self.article_id = article_id
        self.article = Article(self.full_url, self.article_id, save_path)

    def _fill_article_with_text(self, article_soup):
        try:
            self.article.text = article_soup.find(class_='detail_news_text').text.strip()
        except AttributeError as e:
            self.article.text = 'NOT FOUND'

    def _fill_article_with_meta_information(self, article_soup):
        try:
            self.date = article_soup.find_all(class_='detail_info_element')[1].text
            self.date = self.date.strip()
        except AttributeError:
            self.date = '10:00 / 26 марта 2021'
        except IndexError:
            self.date = '10:00 / 26 марта 2021'
        except TypeError:
            self.date = '10:00 / 26 марта 2021'
        self.article.date = ArticleParser.unify_date_format(self.date)
        try:
            date_time_obj = datetime.strptime(self.article.date, '%Y-%m-%d %H:%M:%S')
            self.article.date = date_time_obj
        except ValueError:
            self.date = '10:00 / 26 марта 2021'
            date_time_obj = datetime.strptime(self.article.date, '%Y-%m-%d %H:%M:%S')
            self.article.date = date_time_obj
        try:
            self.article.author = 'NOT FOUND'
            self.article.title = article_soup.find('h3').text
        except AttributeError:
            self.article.title = 'NOT FOUND'
        self.article.topics.append(self.article.title)

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format
        """
        try:
            arr = date_str.split(" ")
            arr[0] = arr[0][0:len(arr[0])]
            res = arr[4] + '-' + get_month(arr[3]) + '-' + arr[2] + ' ' + arr[0] + ':00'
            return res
        except IndexError or AttributeError:
            return "2021-03-26 10:00:00"

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
    recursive_path = os.path.join(base_path, 'tmp', 'recursive')
    if not os.path.exists(recursive_path):
        os.makedirs(recursive_path)


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
    base_urls = json_dict['base_urls']
    total_articles_to_find_and_parse = json_dict['total_articles_to_find_and_parse']
    max_number_articles_to_get_from_one_seed = json_dict['max_number_articles_to_get_from_one_seed']
    return base_urls, total_articles_to_find_and_parse, max_number_articles_to_get_from_one_seed


class CrawlerRecursive(Crawler):
    def __init__(self, seed_url: str, save_path: str = ''):
        super().__init__([seed_url], 0, 0)
        self.urls = []
        self.save_path = save_path
        self.id = 0
        self.parsed = set()

    def run_crawler(self):
        while True:
            self.urls = []
            self.find_articles()
            self.extract_articles(self.get_search_urls())
            self.seed_urls = self.get_search_urls()

    def extract_articles(self, url_list):
        for loop_link in self.get_search_urls():
            if loop_link in self.parsed:
                continue
            self.parsed.add(loop_link)
            loop_article_parser = ArticleParser(loop_link, self.id, self.save_path)
            self.id += 1
            try:
                loop_article_parser.parse()
                loop_article_parser.article.save_raw()
            except ValueError:
                pass

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.urls


if __name__ == '__main__':
    # YOUR CODE HERE

    prepare_environment(constants.PROJECT_ROOT)
    urls, num_urls, max_seed_number = validate_config(constants.CRAWLER_CONFIG_PATH)
    if not constants.RECURSIVE:
        article_id = 1
        for seed in urls:
            print(seed)
            crawler = Crawler(seed_urls=[seed], max_articles=num_urls, max_articles_per_seed=max_seed_number)
            crawler.find_articles()
            for link in crawler.get_search_urls():
                article_parser = ArticleParser(link, article_id)
                article_id += 1
                article_parser.parse()
                article_parser.article.save_raw()
    else:
        CrawlerRecursive(
            seed_url=urls[0],
            save_path=os.path.join(constants.PROJECT_ROOT, 'tmp', 'recursive')
        ).run_crawler()
