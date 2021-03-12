"""
Crawler implementation
"""

import json
import datetime
import os
from time import sleep
import random
import shutil
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from article import Article
from constants import CRAWLER_CONFIG_PATH
from constants import ASSETS_PATH

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
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
    def __init__(self, seed_urls: list, max_articles: int, max_articles_per_seed: int):
        self.seed_urls = seed_urls
        self.max_articles = max_articles
        self.max_articles_per_seed = max_articles_per_seed
        self.urls = []

    @staticmethod
    def _extract_url(article_bs):
        url_article = article_bs.find('div', class_='article-link').find('a')
        link = url_article.attrs['href']
        return 'https://newbur.ru' + link

    def find_articles(self):
        """
        Finds articles
        """
        for url in self.seed_urls:
            response = requests.get(url, headers=headers)
            if not response:
                raise IncorrectURLError
            if response.status_code == 200:
                sleep(random.randrange(2, 6))
            page_soup = BeautifulSoup(response.content, features='lxml')
            article_soup = page_soup.find_all('div', class_='article-info')
            for article_bs in article_soup[:self.max_articles_per_seed]:
                self.urls.append(self._extract_url(article_bs))
                if len(self.urls) == self.max_articles:
                    break
        return self.urls

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
        paragraphs_soup = article_soup.find('div', class_='news-content').find_all('p')
        for parag in paragraphs_soup:
            self.article.text += parag.text.strip() + '\n'

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find('h1').text

        try:
            self.article.author = article_soup.find('div', class_='news-tags').text.strip()
            author_error = self.article.author.split('\n')
            for element in author_error:
                if element == 'Теги:':
                    raise AttributeError
        except AttributeError:
            self.article.author = 'NOT FOUND'
        print(self.article.author)

        self.article.topics = article_soup.find('div', class_='article-details-left')\
            .find('a', class_='article-section').text

        date = article_soup.find('div', class_='article-details-left').find('a', class_='article-date').text
        self.article.date = self.unify_date_format(date)

    @staticmethod
    def unify_date_format(date_str):
        """
        Unifies date format
        """
        months = {'января': 1,
                  'февраля': 2,
                  'марта': 3,
                  'апреля': 4,
                  'мая': 5,
                  'июня': 6,
                  'июля': 7,
                  'августа': 8,
                  'сентября': 9,
                  'октября': 10,
                  'ноября': 11,
                  'декабря': 12}

        date_str = date_str.split(' ')
        if not date_str[0].isdigit():
            today = datetime.today()
            yest = datetime.now() - timedelta(days=1)
            arr = {'Вчера': str(yest.day) + ' ' + str(yest.month) + ' ',
                   'Сегодня': str(today.day) + ' ' + str(today.month) + ' ',
                   'Только': str(today.day) + ' ' + str(today.month)}
            for key in arr:
                if date_str[0] == key:
                    date_str[0] = arr[key]
            if date_str == 'что':
                date_str = str(date_str[0] + ' ' + str(str(today.hour) + ':' + str(today.minute)))
            else:
                date_str = date_str[0] + date_str[-1]
            date_str = date_str.split(' ')
        else:
            for keys in months:
                if keys in date_str[1]:
                    atr = str(months[keys])
                    date_str[1] = atr
        date_str.append(date_str[2])
        date_str[2] = str(datetime.today().year)
        fin = ' '.join(date_str)
        dat = datetime.strptime(fin, '%d %m %Y %H:%M')
        return dat

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
    assets_path = os.path.join(base_path, 'tmp', 'articles')
    if os.path.exists(assets_path):
        shutil.rmtree(os.path.dirname(assets_path))
    os.makedirs(assets_path)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as file:
        config = json.load(file)

    unknown = ('base_urls' not in config or 'total_articles_to_find_and_parse' not in config
               or 'max_number_articles_to_get_from_one_seed' not in config)
    if not isinstance(config, dict) and unknown:
        raise UnknownConfigError

    if not isinstance(config['base_urls'], list) or \
            not all(isinstance(url, str) for url in config['base_urls']):
        raise IncorrectURLError

    if 'total_articles_to_find_and_parse' in config and \
            isinstance(config['total_articles_to_find_and_parse'], int) and \
            config['total_articles_to_find_and_parse'] > 100:
        raise NumberOfArticlesOutOfRangeError

    if 'max_number_articles_to_get_from_one_seed' not in config or \
            not isinstance(config['max_number_articles_to_get_from_one_seed'], int) or \
            'total_articles_to_find_and_parse' not in config or \
            not isinstance(config['total_articles_to_find_and_parse'], int):
        raise IncorrectNumberOfArticlesError
    return config.values()


if __name__ == '__main__':
    # YOUR CODE HERE
    seed_urls_ex, max_articles_ex, max_articles_per_seed_ex = validate_config(CRAWLER_CONFIG_PATH)
    crawler = Crawler(seed_urls=seed_urls_ex, max_articles=max_articles_ex,
                      max_articles_per_seed=max_articles_per_seed_ex)
    art = crawler.find_articles()
    print(art)
    prepare_environment(ASSETS_PATH)
    for ind, article_url in enumerate(crawler.urls):
        parser = ArticleParser(full_url=article_url, article_id=ind + 1)
        article = parser.parse()
        article.save_raw()
        sleep((random.randrange(2, 6)))
