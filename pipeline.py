"""
Pipeline for text processing implementation
"""

import os
from typing import List

from pymystem3 import Mystem
from pymorphy2 import MorphAnalyzer

from constants import ASSETS_PATH
from article import Article


class EmptyDirectoryError(Exception):
    """
    Custom error
    """


class InconsistentDatasetError(Exception):
    """
    Custom error
    """


class UnknownDatasetError(Exception):
    """
    Custom error
    """


class MorphologicalToken:
    """
    Stores language params for each processed token
    """
    def __init__(self, original_word, normalized_form):
        self.normalized_form = normalized_form
        self.original_word = original_word
        self.tags = []
        self.morphy_tags = []

    def __str__(self):
        return f'{self.normalized_form}<{self.tags}>({self.morphy_tags})'


class CorpusManager:
    """
    Works with articles and stores them
    """
    def __init__(self, path_to_raw_txt_data: str):
        self._storage = dict()
        self._path = path_to_raw_txt_data
        self._scan_dataset()

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        for file in os.listdir(self._path):
            if file.endswith('_raw.txt'):
                self._storage[int(file[:-8])] = Article(url=None, article_id=int(file[:-8]))

    def get_articles(self):
        """
        Returns storage params
        """
        return self._storage


class TextProcessingPipeline:
    """
    Process articles from corpus manager
    """
    def __init__(self, corpus_manager: CorpusManager):
        self.corpus_manager = corpus_manager

    def run(self):
        """
        Runs pipeline process scenario
        """
        for article in self.corpus_manager.get_articles().values():
            original_text = article.get_raw_text().lower()
            processed_text = self._process(original_text)
            article.save_processed(' '.join([str(token) for token in processed_text]))

    @staticmethod
    def _process(text) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        analyze = Mystem().analyze(text)
        morph = MorphAnalyzer()
        tokens = []
        for feature in analyze:
            if 'analysis' not in feature or not feature['analysis']:
                continue
            token = MorphologicalToken(feature['text'],
                                       feature['analysis'][0]['lex'])
            token.tags = feature['analysis'][0]['gr']
            token.morphy_tags = morph.parse(token.original_word)[0].tag
            tokens.append(token)
        return tokens


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    if not os.path.exists(path_to_validate):
        raise FileNotFoundError
    if not os.path.isdir(path_to_validate):
        raise NotADirectoryError
    if not os.listdir(path_to_validate):
        raise EmptyDirectoryError


def main():
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager)
    pipeline.run()
    print('Text processing pipeline has just finished')


if __name__ == "__main__":
    main()
