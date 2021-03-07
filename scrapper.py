"""
Crawler implementation
"""
import article
import json
import lxml
import re
import requests

from bs4 import BeautifulSoup
from constants import CRAWLER_CONFIG_PATH
from random import randint
from time import sleep


class UnknownConfigError(Exception):
    """
    Most general error
    """


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


class IncorrectStatusCode(Exception):
    """"
    Custom error
    """


headers = {
        'user-agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'}


class Crawler:
    """
    Crawler implementation
    """

    def __init__(self, seed_urls: list, max_articles: int, max_articles_per_seed: int):
        self.seed_urls = seed_urls
        self.max_articles_per_seed = max_articles_per_seed
        self.max_articles = max_articles
        self.urls = []


    @staticmethod
    def _extract_url(article_bs, urls):
        pages_links = []
        for tag_a_content in article_bs.find_all('div', class_='signature'):
            link = tag_a_content.find('a').get('href')
            if link and link not in urls:
                pages_links.append('http://ks-yanao.ru/' + link)

        return pages_links

        # a = re.findall(r'http://ks-yanao\.ru/\w+/(\w+-)+\w+\.html')

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            try:
                response = requests.get(seed_url, headers=headers)
                sleep(randint(2, 6))
                if response.status_code:
                    main_page_soup = BeautifulSoup(response.content, features='lxml')
                else:
                    raise IncorrectStatusCode
            except IncorrectStatusCode:
                continue
            else:
                found_links = self._extract_url(main_page_soup)
                if len(found_links) < self.max_articles_per_seed:
                    self.urls.extend(found_links)
                else:
                    self.urls.extend(found_links[:self.max_articles_per_seed])

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
        self.article = article.Article(full_url, article_id)

    def _fill_article_with_text(self, article_soup):
        paragraphs_soup = article_soup.find_all('p')
        article_list = [paragraph.text.strip() for paragraph in paragraphs_soup if paragraph.text.strip()]
        article_str = ' '.join(article_list)

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
    with open(crawler_path) as opened_file:
        config = json.load(opened_file)

    is_config_unknown = ('base_urls' not in config
                         or 'total_articles_to_find_and_parse' not in config
                         or 'max_number_articles_to_get_from_one_seed' not in config)
    if not isinstance(config, dict) or is_config_unknown:
        raise UnknownConfigError

    are_urls_incorrect = (not isinstance(config['base_urls'], list)
                          or not all([isinstance(url, str) for url in config['base_urls']]))
    if are_urls_incorrect:
        raise IncorrectURLError

    is_num_articles_incorrect = (not isinstance(config['total_articles_to_find_and_parse'], int)
                                 or not isinstance(config['max_number_articles_to_get_from_one_seed'], int)
                                 or config['total_articles_to_find_and_parse'] < 0
                                 or config['max_number_articles_to_get_from_one_seed'] < 0)
    if is_num_articles_incorrect:
        raise IncorrectNumberOfArticlesError

    is_num_out_of_range = (config['max_number_articles_to_get_from_one_seed'] >
                           config['total_articles_to_find_and_parse'])
    if is_num_out_of_range:
        raise NumberOfArticlesOutOfRangeError

    return config.values()


if __name__ == '__main__':
    # YOUR CODE HERE
    # headers = {
    #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'
    # }
    # response = requests.get(
    #     'http://ks-yanao.ru/proisshestviya/v-novom-urengoe-mikroavtobus-stolknulsya-s-tremya-legkovushkami.html',
    #     headers=headers)
    # page_soup = BeautifulSoup(response.content, features='lxml')
    # header_soup = page_soup.find(class_="element-detail")
    # paragraphs_soup = header_soup.find_all('p')
    # article_list = [paragraph.text.strip() for paragraph in paragraphs_soup if paragraph.text.strip()]
    # article = ' '.join(article_list)
    # print(article)
    # for header in paragraphs_soup:
    #     print(header.text.strip())
    #print(response.text)
    #print(header)


    seed_urls, max_articles, max_articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)
    crawler = Crawler(seed_urls=seed_urls, max_articles=max_articles, max_articles_per_seed=max_articles_per_seed)
    crawler.find_articles()
