"""
Pipeline for text processing implementation
"""

import os
from typing import List
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
    path_to_validate = ASSETS_PATH
    files_check = True
    consistency_check = True

    if not os.path.exists(path_to_validate):
        raise NotADirectoryError

    consistency = os.listdir(path_to_validate)
    if not consistency:
        files_check = False

    if len(consistency) // 2 != 0:
        consistency_check = False

    id_check = True
    files_number = len(consistency) // 2
    ids = []

    for file in consistency:
        ids.append(int(file[0]))
        if len(ids) != files_number:
            id_check = False
        if not file == r'..meta.json' or not file == r'..raw.txt' or not id_check:
            consistency_check = False

    if not consistency_check:
        raise InconsistentDatasetError

    if files_check and consistency_check:
        return None


def main():
    print('Your code goes here')
    validate_dataset(ASSETS_PATH)


if __name__ == "__main__":
    main()
