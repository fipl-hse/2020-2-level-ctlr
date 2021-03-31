"""
Pipeline for text processing implementation
"""
import os
import re

from pymystem3 import Mystem
from pymorphy2 import MorphAnalyzer

from typing import List

from constants import ASSETS_PATH
from article import Article


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
        return f'{self.normalized_form}<{self.mystem_tags}>({self.pymorphy_tags})'

    def __repr__(self):
        pass


class CorpusManager:
    """
    Works with articles and stores them
    """
    def __init__(self, path_to_raw_txt_data: str):
        self.path_to_dataset = path_to_raw_txt_data
        self._storage = self._scan_dataset()

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        storage_dict = {}
        
        for fname in os.listdir(self.path_to_dataset):
            if fname.endswith('_raw.txt'):
                file_id = fname.split('_raw.txt')[0]
                file_id = int(file_id)
                storage_dict[file_id] = Article(url=None, article_id=file_id)

        return storage_dict

    def get_articles(self):
        """
        Returns storage params
        """
        return self._storage

    def __repr__(self):
        pass


class TextProcessingPipeline:
    """
    Process articles from corpus manager
    """
    def __init__(self, corpus_manager: CorpusManager):
        self.corpus_manager = corpus_manager
        self.text = ''

    def run(self):
        """
        Runs pipeline process scenario
        """
        for article in self.corpus_manager.get_articles().values():
            self.text = article.get_raw_text()
            tokens = self._process()
            article.save_processed(' '.join(map(str, tokens)))

    def _process(self) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        tokens = []
        result = Mystem().analyze(self.text)

        for token_dict in result:
            token_text = token_dict['text']
            if token_text.isalnum:
                lemma = token_dict['analysis'][0]['lex'] if 'analysis' in token_dict else token_text
                token = MorphologicalToken(token_text.lower(), lemma)
                if 'analysis' in token_dict:
                    token.mystem_tags = token_dict['analysis'][0]['gr']
                token.pymorphy_tags = token.pymorphy_tags = MorphAnalyzer().parse(token.original_word)[0].tag
                tokens.append(token)

        return tokens

    def __repr__(self):
        pass


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    is_directory = os.path.isdir(path_to_validate)
    if not is_directory:
        if os.path.isfile(path_to_validate):
            raise NotADirectoryError
        raise FileNotFoundError

    is_dir_filled = len(os.listdir(path_to_validate)) > 0
    if not is_dir_filled:
        raise EmptyDirectoryError

    txt_files_num = 0
    json_files_num = 0

    for fname in os.listdir(path_to_validate):
        if re.match(r'^[1-9]\d{0,2}_raw\.txt$', fname):
            txt_files_num += 1
        elif re.match(r'^[1-9]\d{0,2}_meta\.json$', fname):
            json_files_num += 1

    is_dataset_consistent = txt_files_num == json_files_num > 0
    if not is_dataset_consistent:
        raise InconsistentDatasetError

    if is_directory and is_dir_filled and is_dataset_consistent:
        return

    raise UnknownDatasetError


def main():
    # print('Your code goes here')
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
