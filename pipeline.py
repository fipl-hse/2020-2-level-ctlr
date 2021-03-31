"""
Pipeline for text processing implementation
"""

import os
# from typing import List

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


# class MorphologicalToken:
#     """
#     Stores language params for each processed token
#     """
#
#     def __init__(self, original_word, normalized_form):
#         pass
#
#     def __str__(self):
#         return "MorphologicalToken instance here"


# class CorpusManager:
#     """
#     Works with articles and stores them
#     """
#
#     def __init__(self, path_to_raw_txt_data: str):
#         pass
#
#     def _scan_dataset(self):
#         """
#         Register each dataset entry
#         """
#         pass
#
#     def get_articles(self):
#         """
#         Returns storage params
#         """
#         pass


# class TextProcessingPipeline:
#     """
#     Process articles from corpus manager
#     """
#
#     def __init__(self, corpus_manager: CorpusManager):
#         pass
#
#     def run(self):
#         """
#         Runs pipeline process scenario
#         """
#         pass
#
#     def _process(self) -> List[type(MorphologicalToken)]:
#         """
#         Performs processing of each text
#         """
#         pass


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """

    if not os.path.exists(path_to_validate):
        raise NotADirectoryError

    files = os.listdir(path_to_validate)
    if not files:
        raise EmptyDirectoryError

    if len(files) % 2:  # odd number of files
        raise InconsistentDatasetError

    files_number = len(files) // 2
    for i in range(1, files_number + 1):
        if not (os.path.exists(os.path.join(ASSETS_PATH, f'{i}_meta.json'))
                or os.path.exists(os.path.join(ASSETS_PATH, f'{i}_raw.txt'))):
            raise InconsistentDatasetError


def main():
    validate_dataset(ASSETS_PATH)


if __name__ == "__main__":
    main()
