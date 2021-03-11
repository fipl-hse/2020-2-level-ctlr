from bs4 import BeautifulSoup
import json, requests
from constants import CRAWLER_CONFIG_PATH

"""
Crawler implementation
"""


class IncorrectURLError(Exception):
    """
    Custom error
    """
    print("Got incorrect url")


class NumberOfArticlesOutOfRangeError(Exception):
    """
    Custom error
    """
    print("Gut too many articles to download")


class IncorrectNumberOfArticlesError(Exception):
    """
    Custom error
    """
    print("Got incorrect number of articles")


class UnknownConfigError(Exception):
    """
    Most general error
    """
    print("Got incorrect value in config or no value")


class Crawler:
    """
    Crawler implementation
    """
    def __init__(self, seed_urls, num_articles, max_articles):
        self.main_urls = seed_urls
        self.max_articles = max_articles
        self.num_articles = num_articles
        self.urls = []

    @staticmethod
    def _extract_url(article_bs):
        urls = []
        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) '
                                 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Mobile Safari/537.36'}
        req = requests.get(article_bs, headers)
        main_article = BeautifulSoup(req.content, 'html.parser')
        for link in main_article.find_all("a"):
            urls.append(link.get("href"))
        return urls

    def find_articles(self):
        """
        Finds articles
        """
        try:
            for main_url in self.main_urls:
                if len(self.urls) <= self.max_articles:
                    self.urls += Crawler._extract_url(main_url)
        except:
            print(f"error occured")
            return []
        return self.urls[:self.max_articles + 1]


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
    with open(crawler_path, 'r', encoding='utf-8') as file:
        conf = json.load(file)

    if not isinstance(conf, dict) or 'base_urls' not in conf or \
            'max_number_articles_to_get_from_one_seed' not in conf or 'total_articles_to_find_and_parse' not in conf:
        raise UnknownConfigError

    if not isinstance(conf['base_urls'], list) or \
            not all([isinstance(seed_url, str) for seed_url in conf['base_urls']]):
        raise IncorrectURLError

    if not isinstance(conf['total_articles_to_find_and_parse'], int) or \
            not isinstance(conf['max_number_articles_to_get_from_one_seed'], int):
        raise TypeError

    if conf['total_articles_to_find_and_parse'] < 0:
        raise IncorrectNumberOfArticlesError

    if conf['max_number_articles_to_get_from_one_seed'] < 0 or \
            conf['max_number_articles_to_get_from_one_seed'] > conf['total_articles_to_find_and_parse']:
        raise NumberOfArticlesOutOfRangeError

    return conf['max_number_articles_to_get_from_one_seed'], conf['total_articles_to_find_and_parse'], conf["base_urls"]


max_articles, total_number, seed_urls = validate_config(CRAWLER_CONFIG_PATH)
crawler = Crawler(max_articles, total_number, seed_urls)

#crawler.get_search_urls()
print(crawler.find_articles())


if __name__ == '__main__':
    # YOUR CODE HERE
    pass
