"""
Crawler implementation
"""
from time import sleep

import json
import requests
import os
import shutil
from bs4 import BeautifulSoup

from article import Article
from constants import CRAWLER_CONFIG_PATH
from constants import ASSETS_PATH

headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/88.0.4324.190 Mobile Safari/537.36'
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

    def __init__(self, seed_urls: list, max_article: int, max_articles_per_seed: int):
        self.seed_urls = seed_urls
        self.max_article = max_article
        self.max_articles_per_seed = max_articles_per_seed
        self.urls = []

    @staticmethod
    def _extract_url(article_bs):
        return article_bs.find("a").get('href')

    def find_articles(self):
        """
        Finds articles
        """
        main_link = "http://www.kprfast.ru"
        for link in self.seed_urls:
            response = requests.get(link, headers=headers)
            sleep(5)
            print('made request')
            page_soup = BeautifulSoup(response.content, features='lxml')
            all_links = page_soup.find_all(class_="readmore")
            for element in all_links[:max_articles_per_seed]:
                link = self._extract_url(element)
                self.urls.append(main_link + link)
                if len(self.urls) == max_articles:
                    return []

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
        article_text = []
        main_text = article_soup.find('div', itemprop='articleBody')
        article_text.append(main_text.text)
        self.article.text = '\n'.join(article_text)
        return None

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find('a', itemprop='url').text.strip()
        self.article.author = article_soup.find('span', itemprop='name').text
        return None

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
        information = requests.get(self.full_url, headers=headers)
        if information.status_code == 200:
            print('Request is OK')
        else:
            print('Failed request')
        article_bs = BeautifulSoup(information.content, features="lxml")
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
    with open(crawler_path, 'r') as crawler:
        check_config = json.load(crawler)
    all_seed_urls = check_config.get("base_urls")
    all_articles = check_config.get("total_articles_to_find_and_parse")
    max_number = check_config.get("max_number_articles_to_get_from_one_seed", all_articles)

    check_urls = isinstance(all_seed_urls, list)
    check_url = True
    check_number_of_articles = True
    check_range_of_articles = True

    for each_link in all_seed_urls:
        if not isinstance(each_link, str):
            check_url = False

    if not check_urls or not check_url:
        raise IncorrectURLError

    if not isinstance(all_articles, int) or not isinstance(max_number, int) or all_articles == 0 \
            or isinstance(all_articles, bool) or isinstance(max_number, bool):
        check_number_of_articles = False

    if not check_number_of_articles:
        raise IncorrectNumberOfArticlesError

    if all_articles < max_number or max_number < 0 \
            or all_articles > 1000 or all_articles < 0:
        check_range_of_articles = False

    if not check_range_of_articles:
        raise NumberOfArticlesOutOfRangeError

    if check_urls and check_url and check_number_of_articles and check_range_of_articles:
        return all_seed_urls, all_articles, max_number
    else:
        raise UnknownConfigError


if __name__ == '__main__':
    # YOUR CODE HERE
    seed_urls, max_articles, max_articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    check_1 = Crawler(seed_urls, max_articles, max_articles_per_seed)
    check_1.find_articles()
    prepare_environment(ASSETS_PATH)
    for i, url in enumerate(check_1.urls):
        parser = ArticleParser(url, i + 1)
        article = parser.parse()
        article.save_raw()
