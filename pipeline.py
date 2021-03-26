"""
Pipeline for text processing implementation
"""

from typing import List


class EmptyDirectoryError(Exception):
    """
    Custom error
    """


class NotADirectoryError(Exception):
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
    pass


def main():
    print('Your code goes here')


if __name__ == "__main__":
    main()
