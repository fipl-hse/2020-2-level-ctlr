"""
Pipeline for text processing implementation
"""

from typing import List
from constants import ASSETS_PATH

import os


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
    check_files = True
    check_consistency = True

    if not os.path.exists(path_to_validate):
        raise NotADirectoryError

    consistency = os.listdir(path_to_validate)
    if not consistency:
        check_files = False

    if not check_files:
        EmptyDirectoryError

    if len(consistency) // 2 != 0:
        check_consistency = False

    check_id = True
    number_of_files = len(consistency) // 2
    ids = []
    for file in consistency:
        ids.append(int(file[0]))
        if len(ids) != number_of_files:
            check_id = False
        if not file == r'..meta.json' or not file == r'..raw.txt' or not check_id:
            check_consistency = False

    if not check_consistency:
        raise InconsistentDatasetError

    if check_files and check_consistency:
        return None
    else:
        UnknownDatasetError



def main():
    print('Your code goes here')
    validate_dataset(ASSETS_PATH)

if __name__ == "__main__":
    main()
