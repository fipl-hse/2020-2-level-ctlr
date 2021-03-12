"""
Crawler implementation
"""
from bs4 import BeautifulSoup
import requests
import time
from urllib.parse import urljoin, urldefrag


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
    # def __init__(self, ):


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


class Crawler:
    """
    Crawler implementation
    """
    lw = LinkWorker('', '')

    def __init__(self, seed_urls: list, max_articles: int):
        self.seed_urls = seed_urls
        self.max_articles = max_articles

    @staticmethod
    def _extract_url(article_bs):
        new_seed_urls = []
        for a in article_bs.find_all('a'):
            link = str(a.get('href'))
            if link.find('https://') == -1:
                try:
                    Crawler.lw.update_link(link)
                    new_seed_urls.append(Crawler.lw.get_absolute_link())
                except:
                    pass
            else:
                try:
                    new_seed_urls.append(link)
                except:
                    pass

    def find_articles(self):
        """
        Finds articles
        """
        new_urls = []

        for url in self.get_search_urls():
            time.sleep(0.25)
            try:
                response = requests.get(self.get_search_urls())
                parser = BeautifulSoup(response.text, 'lxml')
                self.lw = LinkWorker(url, "")
                new_urls.extend(self._extract_url(parser))
            except Exception:
                raise IncorrectURLError

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
    pass
