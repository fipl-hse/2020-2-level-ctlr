"""
Pipeline for text processing implementation
"""

import os
import re

from typing import List


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
        pass

    def __str__(self):
        return "MorphologicalToken instance here"


class CorpusManager:
    """
    Works with articles and stores them
    """
    def __init__(self, path_to_raw_txt_data: str):
        pass

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        pass

    def get_articles(self):
        """
        Returns storage params
        """
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


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    is_dataset_exists = True
    # dataset exists (there is a folder)
    if not os.path.exists(path_to_validate):
        is_dataset_exists = False
        raise FileNotFoundError
    if not os.path.isdir(path_to_validate):
        raise NotADirectoryError

    files = os.listdir(path_to_validate)
    # dataset is not empty (there are files inside)
    is_dataset_not_empty = True
    if not files:
        is_dataset_not_empty = False
        raise EmptyDirectoryError

    # dataset is balanced: there are only files that follow the naming conventions:
    is_dataset_balanced = True
    for file in files:
        # N_raw.txt, N_meta.json, where N is a valid number
        try:
            is_number_valid = int(file[0])
        except ValueError:
            is_dataset_balanced = False
            raise InconsistentDatasetError
        # Numbers of articles are from 1 to N without any slips
        n = 1
        if file == r'..raw.txt' and int(file[0]) != n:
            is_dataset_balanced = False
            raise InconsistentDatasetError
        n += 1
    if is_dataset_exists and is_dataset_not_empty and is_dataset_balanced:
        return None
    else:
        raise UnknownDatasetError


def main():
    print('Your code goes here')
    from constants import ASSETS_PATH
    validate_dataset(ASSETS_PATH)


if __name__ == "__main__":
    main()
