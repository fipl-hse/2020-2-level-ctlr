"""
Pipeline for text processing implementation
"""
import os
from typing import List
from constants import ASSETS_PATH
from pathlib import Path


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
        self.res_mystem = ''
        self.res_pymorphy = ''

    def __str__(self):
        return '{normalized_form}<{mystem}>({pymorphy})'.format(normalized_form=self.normalized_form,
                                                                mystem=self.res_mystem,
                                                                pymorphy=self.res_pymorphy)

    def some_public_method(self):
        pass


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
        pass

    def get_articles(self):
        """
        Returns storage params
        """
        return self._storage

    def some_public_method(self):
        pass


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

    def some_public_method(self):
        pass


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
    corpus_manager = CorpusManager(path_to_dataset=ASSETS_PATH)

if __name__ == "__main__":
    main()
