"""
Pipeline for text processing implementation
"""


class ArticleNotFoundError(Exception):
    """
    Custom error
    """


class EmptyDirectoryError(Exception):
    """
    Custom error
    """


class MorphologicalToken:
    """
    Stores language params for each processed token
    """
    def __init__(self, normalized_form, tags, original_word):
        pass

    def to_text(self):
        """
        Converts instance to str format
        """

    def __str__(self):
        pass


class CorpusManager:
    """
    Works with articles and stores them
    """
    def __init__(self, path_to_raw_txt_data: str):
        pass

    def get_articles_meta(self):
        """
        Gets article metadata
        """

    def get_raw_text(self, text_id):
        """
        Opens processed text
        """

    def write_processed_text(self, text_id, processed_text):
        """
        Writes processed text
        """


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

    @staticmethod
    def normalize_and_tag_text(text) -> str:
        """
        Processes each token and creates MorphToken class instance
        """

    @staticmethod
    def transform_tokens_to_text(tokens: list) -> str:
        """
        Transforms given list of tokens to str
        """


def validate_given_path(path_to_validate):
    """
    Validates folder with assets
    """
    return path_to_validate


if __name__ == "__main__":
    # YOUR CODE HERE
    pass
