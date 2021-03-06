"""
Crawler implementation
"""

import requests
from time import sleep
from bs4 import BeautifulSoup

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
    def __init__(self, seed_urls: list, max_articles=1):
        self.seed_urls = seed_urls

    @staticmethod
    def _extract_url(article_bs):
        pass

    def find_articles(self):
        """
        Finds articles
        """
        for url in self.seed_urls:
            response = requests.get(url)
            sleep(5)
            print('good')

        return [response]

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
    headers = {'Use-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.41 YaBrowser/21.2.0.1097 Yowser/2.5 Safari/537.36'}
    response = requests.get('https://ugra-news.ru/article/andrey_filatov_vstupil_v_dolzhnost_glavy_surguta/',
                            headers=headers)
    print('good')

    page_bs = BeautifulSoup(response.content, features='lxml')

    header_soup = page_bs.find_all(name='h1')

    for line in header_soup:
        print('Tag name: {}'.format(line.name))
        print('Tag text:',format(line.text))

    article_content = page_bs.find(name='div', class_="col_content")
    print(article_content)
    #print(article.text for article in article_contetnt)

    '''sleep(5)

    with open(file='text.html', mode='w', encoding='utf-8') as f:
        f.write(response.text)

    with open(file='text.html', mode='r', encoding='utf-8') as f:
        print(f.read())
    print(response.request.headers)'''

    #test = Crawler(['https://ugra-news.ru/', 'https://ugra-news.ru/article/andrey_filatov_vstupil_v_dolzhnost_glavy_surguta/'])
    #all_articles = test.find_articles()

