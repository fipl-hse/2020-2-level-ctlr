"""
Article implementation
"""
import json
import os
import datetime

from constants import ASSETS_PATH


def date_from_meta(date_txt):
    """
    Converts text date to datetime object
    """
    return datetime.datetime.strptime(date_txt, "%Y-%m-%d %H:%M:%S")


class Article:
    """
    Article class implementation.
    Stores article metadata and knows how to work with articles
    """
    def __init__(self, url, article_id):
        self.url = url
        self.article_id = article_id

        self.title = ''
        self.date = None
        self.author = ''
        self.topics = []
        self.text = ''

    def save_raw(self):
        """
        Saves raw text and article meta data
        """
        article_meta_name = "{}_meta.json".format(self.article_id)

        with open(self._get_raw_text_path(), 'w', encoding='utf-8') as file:
            file.write(self.text)

        with open(os.path.join(ASSETS_PATH, article_meta_name), "w", encoding='utf-8') as file:
            json.dump(self._get_meta(),
                      file,
                      sort_keys=False,
                      indent=4,
                      ensure_ascii=False,
                      separators=(',', ': '))

    @staticmethod
    def from_meta_json(json_path: str):
        """
        Loads meta.json file and writes its data
        """
        with open(json_path, encoding='utf-8') as meta_file:
            meta = json.load(meta_file)

        url = meta.get('url', None)
        article_id = meta.get('id', None)
        article = Article(url, article_id)
        article.title = meta.get('url', '')
        article.date = date_from_meta(meta.get('date', None))
        article.author = meta.get('author', None)
        article.topics = meta.get('topics', None)

        # intentionally leave it empty
        article.text = None

        return article

    def get_raw_text(self):
        """
        Gets a raw text for requested article
        """
        with open(self._get_raw_text_path(), encoding='utf-8') as file:
            return file.read()

    def save_processed(self, processed_text):
        """
        Saves processed article text
        """
        with open(self._get_processed_text_path(), 'w', encoding='utf-8') as file:
            file.write(processed_text)

    def _get_meta(self):
        """
        Gets all article params
        """
        return {
            'id': self.article_id,
            'url': self.url,
            'title': self.title,
            'date': self._date_to_text(),
            'author': self.author,
            'topics': self.topics
        }

    def _date_to_text(self):
        """
        Converts datetime object to text
        """
        return self.date.strftime("%Y-%m-%d %H:%M:%S")

    def _get_raw_text_path(self):
        """
        Returns path for requested raw article
        """
        article_txt_name = "{}_raw.txt".format(self.article_id)
        return os.path.join(ASSETS_PATH, article_txt_name)

    def _get_processed_text_path(self):
        """
        Returns path for requested processed article
        """
        article_txt_name = "{}_processed.txt".format(self.article_id)
        return os.path.join(ASSETS_PATH, article_txt_name)
