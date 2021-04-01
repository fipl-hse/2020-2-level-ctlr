# pylint: disable=R0903
"""
Pipeline for text processing implementation
"""

import re
from pathlib import Path
from typing import List

from pymorphy2 import MorphAnalyzer
from pymystem3 import Mystem

from article import Article
from constants import ASSETS_PATH
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
        self.mystem_tags = ''
        self.pymorphy_tags = ''
        self.original_word = original_word
        self.normalized_form = normalized_form

    def __str__(self):
        return f"{self.normalized_form}<{self.mystem_tags}>({self.pymorphy_tags})"


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
        for file in Path(self.path_to_raw_txt_data).glob('*_raw.txt'):
            file_id = str(file).split('\\')[-1].split('_')[0]
            # file_id = re.search(r'\d+', str(file).split('\\')[-1]).group()
            self._storage[file_id] = Article(url=None, article_id=file_id)

    def get_articles(self):
        """
        Returns storage params
        """
        return self._storage


class TextProcessingPipeline:
    """
    Process articles from corpus manager
    """
    def __init__(self, corpus_manager: CorpusManager):
        self.corpus_manager = corpus_manager
        self._text = ''

    def run(self):
        """
        Runs pipeline process scenario
        """
        for article in tuple(self.corpus_manager.get_articles().values()):
            self._text = article.get_raw_text()
            tokens = self._process()
            article.save_processed(' '.join(tokens))

    def _process(self) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        tokens = []
        result = Mystem().analyze(self._text)
        for word in tuple(result):
            try:
                token = MorphologicalToken(original_word=word['text'].lower(),
                                           normalized_form=word['analysis'][0]['lex'])
                token.mystem_tags = word['analysis'][0]['gr']
                token.pymorphy_tags = MorphAnalyzer().parse(word['text'])[0].tag
            except (KeyError, IndexError):
                continue
            tokens.append(str(token))
        return tokens


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    # FileNotFoundError, NotADirectoryError, InconsistentDatasetError, EmptyDirectoryError, UnknownDatasetError
    path = Path(path_to_validate)

    if not path.is_dir():
        if path.is_file():
            raise NotADirectoryError
        raise FileNotFoundError

    if not any(path.iterdir()):
        raise EmptyDirectoryError


def main():
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)

    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    pipeline.run()

    pos_pipeline = POSFrequencyPipeline(corpus_manager=corpus_manager)
    pos_pipeline.run()


if __name__ == "__main__":
    main()
