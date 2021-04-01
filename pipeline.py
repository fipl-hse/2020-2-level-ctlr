"""
Pipeline for text processing implementation
"""

import os
import re
from pymystem3 import Mystem
from article import Article

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
        self.original_word = original_word
        self.normalized_form = normalized_form
        self.mystem_tags = ''
        self.pymorphy_tags = ''

    def __str__(self):
        return self.normalized_form


class CorpusManager:
    """
    Works with articles and stores them
    """

    def __init__(self, path_to_raw_txt_data: str):
        self.path_to_raw_txt_data = path_to_raw_txt_data
        self._storage = {}

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        files = os.listdir(self.path_to_raw_txt_data)
        for file in files:
            ind_underscore = file.index('_')
            is_raw_txt = re.match(r'.+_raw\.txt', file)
            if is_raw_txt:
                self._storage[int(file[:ind_underscore])] = Article(url=None, article_id=int(file[:ind_underscore]))
        return None

    def get_articles(self):
        """
        Returns storage params
        """
        self._scan_dataset()
        return self._storage.values()


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
        articles = self.corpus_manager.get_articles()
        for article in articles:
            raw_text_article = article.get_raw_text()
            result = Mystem().analyze(raw_text_article)
            tokens = self._process(mystem_analize_result=result)  # list with instances MorphToken
            processed_text_tokens = []
            for token in tokens:
                processed_text_tokens.append('{}{}'.format(token.__str__(), token.mystem_tags))
            processed_text = ' '.join(processed_text_tokens)
            article.save_processed(processed_text)
        return None

    def _process(self, mystem_analize_result) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        tokens = []
        for element in mystem_analize_result:
            if element.get('analysis') is None:
                continue
            if not element.get('analysis'):
                token = MorphologicalToken(original_word=element['text'], normalized_form=element['text'])
                token.mystem_tags = '<>'
            else:
                token = MorphologicalToken(original_word=element['text'],
                                           normalized_form=element['analysis'][0].get('lex'))
                token.mystem_tags = '<{}>'.format(element['analysis'][0].get('gr'))
            tokens.append(token)
        return tokens


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    # dataset exists
    is_dataset_exists = True
    if not os.path.exists(path_to_validate):
        is_dataset_exists = False
        raise FileNotFoundError
    is_directory = True
    if not os.path.isdir(path_to_validate):
        is_directory = False
        raise NotADirectoryError

    files = os.listdir(path_to_validate)
    # dataset is not empty (there are files inside)
    is_dataset_not_empty = True
    if not files:
        is_dataset_not_empty = False
        raise EmptyDirectoryError

    # dataset is balanced: there are only files that follow the naming conventions:
    is_dataset_balanced = True
    n = 0
    for file in files:
        ind_underscore = file.index('_')
        # N_raw.txt, N_meta.json, where N is a valid number
        try:
            is_number_valid = int(file[:ind_underscore])
        except ValueError:
            is_dataset_balanced = False
            raise InconsistentDatasetError
        # Numbers of articles are from 1 to N without any slips
        if re.match(r'.+_raw\.txt', file):
            n += 1
            if int(file[:ind_underscore]) != n:
                is_dataset_balanced = False
                raise InconsistentDatasetError

    if is_dataset_exists and is_directory and is_dataset_not_empty and is_dataset_balanced:
        return None
    else:
        raise UnknownDatasetError


def main():
    print('Your code goes here')
    from constants import ASSETS_PATH

    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
