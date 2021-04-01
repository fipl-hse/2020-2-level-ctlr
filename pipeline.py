"""
Pipeline for text processing implementation
"""
import os
from typing import List

import pymorphy2
from pymystem3 import Mystem

from article import Article
from constants import ASSETS_PATH


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
        self.original_word = original_word
        self.normalized_form = normalized_form
        self.mystem_tags = ''
        self.pymorpy_tags = ''

    def __str__(self):
        return "MorphologicalToken instance here"


class CorpusManager:
    """
    Works with articles and stores them
    """
    def __init__(self, path_to_raw_txt_data: str):
        self.path_to_raw_txt_data = path_to_raw_txt_data
        self._storage = {}
        self._scan_dataset()

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        last = len(os.listdir(self.path_to_raw_txt_data)) // 2
        for i in range(1, last + 1):
            self._storage[i] = Article(url=None, article_id=i)

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

        pass

    def run(self):
        """
        Runs pipeline process scenario
        """
        pass

    def _process(self) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        pass


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    if not os.path.exists(path_to_validate):
        raise FileNotFoundError

    files = os.listdir(path_to_validate)
    if not files:
        raise EmptyDirectoryError

    if not os.path.isdir(path_to_validate):
        raise NotADirectoryError

    if len(files) % 2:
        raise InconsistentDatasetError

    files_number = len(files) // 2
    for i in range(1, files_number + 1):
        if not (os.path.exists(os.path.join(path_to_validate, f'{i}_meta.json'))
                or os.path.exists(os.path.join(path_to_validate, f'{i}_raw.txt'))):
            raise InconsistentDatasetError


def main():
    # print('Your code goes here')
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
