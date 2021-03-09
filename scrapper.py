"""
Crawler implementation
"""
import requests
from bs4 import BeautifulSoup
from constants import CRAWLER_CONFIG_PATH
import json
from time import sleep
import article


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

    @staticmethod
    def _extract_url(article_bs):
        pass

    def find_articles(self):
        """
        Finds articles
        """
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'
        }
        for seed_url in self.seed_urls:
            response = requests.get(seed_url, headers=headers)
            sleep(5)

            if response.status_code == 200:
                seed_url_soup = BeautifulSoup(response.content, features='lxml')
                future_article_links_soup = seed_url_soup.find_all(class_="grow_single")
                future_article_links_soup = future_article_links_soup[0:self.max_articles_per_seed]
                for future_article_link in future_article_links_soup:
                    self.urls.append(future_article_link.find('a').get('href'))

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
        self.article.date = date.text

        self.article.author = 'No author'

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
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'
        }
        response = requests.get(self.full_url, headers=headers)
        if response.status_code == 200:
            article_bs = BeautifulSoup(response.content, features='lxml')
            self._fill_article_with_text(article_bs)
            self._fill_article_with_meta_information(article_bs)
        article.save_raw()
        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    pass


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

    return initial_values["base_urls"], initial_values["total_articles_to_find_and_parse"], \
           initial_values["max_number_articles_to_get_from_one_seed"]


if __name__ == '__main__':
    # YOUR CODE HERE

    # step 1
    seed_urls, max_articles, max_articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)

    # step 2.1
    crawler = Crawler(seed_urls=seed_urls, total_max_articles=max_articles, max_articles_per_seed=max_articles_per_seed)

    # step 2.2
    crawler.find_articles()

    # step 3.1, 3.2, 3.3, 4, 5
    for url_id, url in enumerate(crawler.urls):
        parser = ArticleParser(full_url=url, article_id=url_id)
        parsed_article = parser.parse()
        sleep(5)
