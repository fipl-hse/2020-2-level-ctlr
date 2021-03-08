"""
Crawler implementation
"""

import json
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from time import sleep as wait
from article import Article


CRAWLER_CONFIG_PATH = 'crawler_config.json'

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
    def __init__(self, seed_urls: list, total_max_articles: int, max_articles_per_seed: int):
        self.seed_urls = seed_urls
        self.total_max_articles = total_max_articles
        self.max_articles_per_seed = max_articles_per_seed
        self.urls = []

        self.URL_START = 'https://burunen.ru'

    @staticmethod
    def _extract_url(article_bs, seen):
        extracted = list(set([link['href'] for link in article_bs.find_all('a', href=True)]))
        # print(extracted)
        # print('          ',extracted)
        return list(filter(lambda x: True if x.startswith('/news/')
                           and x not in seen
                           # and any(map(lambda y: y.isdigit(), x))
                           else False, extracted))

    def find_articles(self):
        """
        Finds articles
        """
        for url in self.seed_urls:
            article_bs = BeautifulSoup(requests.get(url, 'html.parser').text, 'html.parser')
            newfound = self._extract_url(article_bs, self.urls)
            self.urls.extend(newfound[:self.max_articles_per_seed])
        self.urls = [i for i in self.urls if len(i) > 20][:self.total_max_articles]
        print('Scraped seed urls, overall number of urls is', len(self.urls))

        old = len(self.urls)
        while len(self.urls) < self.total_max_articles:
            print('Due to insufficient number started further iteration')
            print('current number', len(self.urls), ', required', self.total_max_articles)
            for url in self.urls:
                article_bs = BeautifulSoup(requests.get(self.URL_START + url, 'html.parser').text, 'html.parser')
                newfound = filter(lambda x: len(x) > 20, self._extract_url(article_bs, self.urls))
                print('    checked new url, found', len(newfound), 'articles')
                self.urls.extend(newfound[:self.max_articles_per_seed])
                # wait(10)
                if len(self.urls) > self.total_max_articles:
                    break
            if len(self.urls) == old:
                print('Something is wrong with scraping parameters')
                break

            self.urls = self.urls[:self.total_max_articles]


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
        self.article = Article(self.full_url, self.article_id)

    def _fill_article_with_text(self, article_soup):
        all_text = article_soup.find('div', {'class' : 'text letter', 'itemprop' : 'articleBody'}).text
        text = (all_text..split('Автор:')[0].strip())
        self.text = text

    def _fill_article_with_meta_information(self, article_soup):
        pass

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
        html = requests.get(self.full_url, 'html.parser').text
        article_bs = BeautifulSoup(html, 'html.parser')
        self._fill_article_with_text(article_bs)
        # self._fill_article_with_text(article_bs)
        # self._fill_article_with_meta_information(article_bs)


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    pass


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as crawler_config:
        config = json.load(crawler_config)
    try:
        good_response = list(map(lambda link: True if requests.get(link).status_code == 200 else False,
                                 config['base_urls']))
    except RequestException:
        raise IncorrectURLError
    except Exception:
        raise UnknownConfigError
    if not all(good_response):
        raise IncorrectURLError
    if not all((isinstance(config['total_articles_to_find_and_parse'], int),
                isinstance(config['max_number_articles_to_get_from_one_seed'], int))):
        raise IncorrectNumberOfArticlesError
    if not config['total_articles_to_find_and_parse'] < config['max_number_articles_to_get_from_one_seed']\
       * len(good_response):
        raise NumberOfArticlesOutOfRangeError
    return config['base_urls'], config['total_articles_to_find_and_parse'], \
        config['max_number_articles_to_get_from_one_seed']


if __name__ == '__main__':
    seed_urls, max_articles, max_articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    crawler = Crawler(seed_urls=seed_urls,
                      total_max_articles=max_articles,
                      max_articles_per_seed=max_articles_per_seed)

    crawler.find_articles()
    print('Scraped', len(crawler.urls), 'articles')

    print('onto parsing')

    for n, url in enumerate(crawler.urls[:1]):
        full_url = crawler.URL_START + url
        parser = ArticleParser(full_url, n)
        article = parser.parse()
