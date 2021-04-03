"""
Pipeline for text processing implementation
"""
import re
import pathlib

from typing import List

from pymystem3 import Mystem
from pymorphy2 import MorphAnalyzer

from constants import ASSETS_PATH
from article import Article
from pos_frequency_pipeline import POSFrequencyPipeline


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

        for path in pathlib.Path(self.path_to_dataset).glob('*_raw.txt'):
            fname = path.name
            file_id = fname.split('_')[0]
            if file_id.isdigit() and 0 <= int(file_id) <= 1000:
                storage_dict[int(file_id)] = Article(url=None, article_id=file_id)

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
            if 'analysis' in token_dict and token_dict['analysis'] and 'lex' in token_dict['analysis'][0]:
                token = MorphologicalToken(token_dict['text'].lower(), token_dict['analysis'][0]['lex'])
                token.mystem_tags = token_dict['analysis'][0].get('gr', '')
                tokens.append(token)

        for token in tokens:
            result_pymorphy = MorphAnalyzer().parse(token.original_word)
            if result_pymorphy:
                try:
                    token.pymorphy_tags = result_pymorphy[0].tag
                except AttributeError:
                    continue

        return tokens

    def __repr__(self):
        pass


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    is_directory = pathlib.Path(path_to_validate).is_dir()
    if not is_directory:
        if pathlib.Path(path_to_validate).is_file():
            raise NotADirectoryError
        raise FileNotFoundError

    is_dir_filled = len(list(pathlib.Path(path_to_validate).glob('*'))) > 0
    if not is_dir_filled:
        raise EmptyDirectoryError

    txt_files_num = 0
    json_files_num = 0

    for path in pathlib.Path(path_to_validate).glob('*'):
        fname = path.name
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
    pos_freq_pipeline = POSFrequencyPipeline(corpus_manager)
    pos_freq_pipeline.run()


if __name__ == "__main__":
    main()
