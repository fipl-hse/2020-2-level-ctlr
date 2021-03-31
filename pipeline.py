"""
Pipeline for text processing implementation
"""

from typing import List
import os
import article
from pathlib import Path
from pymystem3 import Mystem
from constants import ASSETS_PATH  # распределить !!!!!!!!!!


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
        self.pymorphy_tags = ''

    def __str__(self):
        return "MorphologicalToken instance here"
        # return "{}<{}>({})".format(self.normalized_form, self.mystem_tags, self.pymorphy_tags)


class CorpusManager:
    """
    Works with articles and stores them
    """
    def __init__(self, path_to_raw_txt_data: str):
        self.path_to_data = path_to_raw_txt_data
        self._storage = {}

        self._scan_dataset()

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        data_content = os.listdir(self.path_to_data)
        for file_content in data_content:
            if '_raw' in file_content:
                key_number = int(file_content[0])
                self._storage[key_number] = article.Article(url=None, article_id=key_number)

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

    if not isinstance(path_to_validate, str):
        raise UnknownDatasetError

    if os.path.exists(path_to_validate):

        dir_content = os.listdir(path_to_validate)
        if not dir_content:
            raise EmptyDirectoryError

        if not Path(path_to_validate).is_dir():
            raise NotADirectoryError

        #if
           # raise InconsistentDatasetError

    return None


def main():
    print('Your code goes here')
    validate_dataset(ASSETS_PATH)  # step 1
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)  # step 2
    token = MorphologicalToken(original_word, normalized_form)  # step 3 ???
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)  # step 4


if __name__ == "__main__":
    main()
