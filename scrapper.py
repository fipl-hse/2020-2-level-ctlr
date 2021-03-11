"""
Crawler implementation
"""
import json
import os
import datetime
from time import sleep
import shutil
import requests
from bs4 import BeautifulSoup
import article
from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH, headers


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
    def __init__(self, seed_urls_: list, total_max_articles: int, max_articles_per_one_seed: int):
        self.seed_urls_ = seed_urls_
        self.total_max_articles = total_max_articles
        self.max_articles_per_one_seed = max_articles_per_one_seed
        self.urls = []

    @staticmethod
    def _extract_url(article_bs, max_articles_per_one_seed, urls):
        future_article_links_soup = article_bs.find_all(class_="grow_single")
        future_article_links_soup = future_article_links_soup[0:max_articles_per_one_seed]
        for future_article_link in future_article_links_soup:
            urls.append(future_article_link.find('a').get('href'))

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls_:
            response = requests.get(seed_url, headers=headers)
            sleep(5)

            if response.status_code == 200:
                seed_url_soup = BeautifulSoup(response.content, features='lxml')
                self._extract_url(seed_url_soup, self.max_articles_per_one_seed, self.urls)

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
        self.article = article.Article(full_url, article_id)

    def _fill_article_with_text(self, article_bs):
        article_text_list = []
        article_main_text_soup = article_bs.find(class_="video-show")
        article_paragraphs_soup = article_main_text_soup.find_all('p')
        for paragraph in article_paragraphs_soup:
            article_text_list.append(paragraph.text)
        article_text = "\n".join(article_text_list)
        self.article.text = article_text

    def _fill_article_with_meta_information(self, article_soup):
        title = article_soup.find('h1')
        self.article.title = title.text

        date = article_soup.find('p', class_="date-time")
        self.article.date = self.unify_date_format(date.text)

        self.article.author = 'NOT FOUND'

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format
        """
        month_dict = {'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5, 'июня': 6, 'июля': 7,
                      'августа': 8, 'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12}

        date, week_day, time = date_str.split(',')

        day, month, year = date.split(' ')  # дата
        day = int(day)
        year = int(year)
        for key, value in month_dict.items():
            if month == key:
                month = value

        hour, minute = time.split(':')  # время
        hour = int(hour)
        minute = int(minute)

        new_date = datetime.datetime(year, month, day, hour, minute)
        return new_date

    def parse(self):
        """
        Parses each article
        """
        response = requests.get(self.full_url, headers=headers)
        if response.status_code == 200:
            article_bs = BeautifulSoup(response.content, features='lxml')
            self._fill_article_with_text(article_bs)
            self._fill_article_with_meta_information(article_bs)
        self.article.save_raw()
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
    with open(crawler_path, 'r', encoding='utf-8') as f:
        initial_values = json.load(f)

    for base_url in initial_values["base_urls"]:
        if not isinstance(base_url, str):
            raise IncorrectURLError

    if not initial_values["base_urls"]:
        raise IncorrectURLError

    if not isinstance(initial_values["total_articles_to_find_and_parse"], int):
        raise IncorrectNumberOfArticlesError

    if initial_values["total_articles_to_find_and_parse"] <= 0 \
            or initial_values["total_articles_to_find_and_parse"] > 100:
        raise NumberOfArticlesOutOfRangeError

    if not isinstance(initial_values["max_number_articles_to_get_from_one_seed"], int) \
            or initial_values["max_number_articles_to_get_from_one_seed"] <= 0 \
            or initial_values["max_number_articles_to_get_from_one_seed"] > 100:
        raise UnknownConfigError

    return (initial_values["base_urls"],
            initial_values["total_articles_to_find_and_parse"],
            initial_values["max_number_articles_to_get_from_one_seed"])


if __name__ == '__main__':
    # YOUR CODE HERE
    prepare_environment(ASSETS_PATH)

    # step 1
    seed_urls, max_articles, max_articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)

    # step 2.1
    crawler = Crawler(seed_urls_=seed_urls, total_max_articles=max_articles,
                      max_articles_per_one_seed=max_articles_per_seed)

    # step 2.2
    crawler.find_articles()

    # step 3.1, 3.2, 3.3, 4, 5, 6, 7
    for url_id, url in enumerate(crawler.urls):
        parser = ArticleParser(full_url=url, article_id=url_id + 1)
        parsed_article = parser.parse()
        sleep(5)
