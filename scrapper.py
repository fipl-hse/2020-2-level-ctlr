"""
Crawler implementation
"""
import requests
from bs4 import BeautifulSoup
from time import sleep
import lxml


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


class Crawler:
    """
    Crawler implementation
    """
    def __init__(self, seed_urls: list, max_articles: int):
        pass

    @staticmethod
    def _extract_url(article_bs):
        pass

    def find_articles(self):
        """
        Finds articles
        """
        pass

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
        pass

    def _fill_article_with_text(self, article_soup):
        pass

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
        pass


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    pass


def validate_config(crawler_path):
    """
    Validates given config
    """
    pass


if __name__ == '__main__':
    # YOUR CODE HERE
    # response = requests.get('http://ks-yanao.ru/novosti/v-labytnangi-priznayut-sgorevshiy-dom-avariynym.html')
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'
    }
    response = requests.get('http://ks-yanao.ru/proisshestviya/v-novom-urengoe-mikroavtobus-stolknulsya-s-tremya-legkovushkami.html',
                              headers=headers)
    page_soup = BeautifulSoup(response.content, features='lxml')
    header_soup = page_soup.find(class_="element-detail")
    paragraphs_soup = header_soup.find_all('p')
    # header = header_soup.text
    for header in paragraphs_soup:
        print(f'**{header.text.strip()}**')
    # print(response.text)
    # print(header)
