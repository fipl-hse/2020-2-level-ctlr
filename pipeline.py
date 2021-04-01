"""
Pipeline for text processing implementation
"""

from pathlib import Path
import re
from typing import List

import pymorphy2
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
        self.original_word = original_word
        self.normalized_form = normalized_form
        self.mystem_tags = ''
        self.pymorpy_tags = ''

    def __str__(self):
        return f"{self.normalized_form}<{self.mystem_tags}>({self.pymorpy_tags})"


class CorpusManager:
    """
    Works with articles and stores them
    """

    def __init__(self, path_to_raw_txt_data: str):
        self.path_to_raw_txt_data = path_to_raw_txt_data
        self._storage = self._scan_dataset()

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        storage = {}
        i = 1
        for filename in Path(self.path_to_raw_txt_data).iterdir():
            if re.fullmatch(r'\d+_raw.txt', str(filename)):
                storage[i] = Article(url=None, article_id=i)
                storage[i].text = storage[i].get_raw_text()
                i += 1
        return storage

    def get_articles(self):
        """
        Returns storage params
        """
        return self._storage


class TextProcessingPipeline:
    """
    Process articles from corpus manager
    """

    def __init__(self, corpus_manager):
        self.corpus_manager = corpus_manager
        self._current_article = None

    def run(self):
        """
        Runs pipeline process scenario
        """
        articles = self.corpus_manager.get_articles()
        for article in articles.values():
            self._current_article = article
            tokens = self._process()
            tokens = ' '.join([str(token) for token in tokens])
            article.save_processed(tokens)

    def _process(self) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        morph = pymorphy2.MorphAnalyzer()

        text = self._current_article.text
        text = ' '.join(re.findall(r'\w+', text.lower()))
        result = Mystem().analyze(text)
        tokenized_text = []

        for word in result[::2]:  # skip whitespaces
            if 'analysis' not in word or word['analysis'] == []:
                continue

            original = word['text']
            normalized = word['analysis'][0]['lex']
            tags = word['analysis'][0]['gr']

            token = MorphologicalToken(original, normalized)
            token.mystem_tags = tags

            if pymorpy_res := morph.parse(original):
                token.pymorpy_tags = pymorpy_res[0].tag

            tokenized_text.append(token)
        return tokenized_text


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    path_to_validate = Path(path_to_validate)

    if not path_to_validate.exists():
        raise FileNotFoundError

    if not any(True for _ in path_to_validate.iterdir()):
        raise EmptyDirectoryError

    if not path_to_validate.is_dir():
        raise NotADirectoryError

    max_files_number = max(len(list(path_to_validate.glob('*.txt'))),
                           len(list(path_to_validate.glob('*.json'))))
    prev_not_exists = False
    for i in range(1, max_files_number + 1):
        raw_path = path_to_validate / f'{i}_raw.txt'
        meta_path = path_to_validate / f'{i}_meta.json'

        if raw_path.exists() and meta_path.exists() and not prev_not_exists:
            continue
        if not raw_path.exists() and not meta_path.exists():
            prev_not_exists = True
            continue
        raise InconsistentDatasetError


def main():
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    processing_pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    processing_pipeline.run()
    pos_pipeline = POSFrequencyPipeline(corpus_manager=corpus_manager)
    pos_pipeline.run()


if __name__ == "__main__":
    main()
