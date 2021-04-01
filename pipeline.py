"""
Pipeline for text processing implementation
"""

import os
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
        for filename in os.listdir(self.path_to_raw_txt_data):
            if re.fullmatch(r'\d+_raw.txt', filename):
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

    if not os.path.exists(path_to_validate):
        raise FileNotFoundError

    files = os.listdir(path_to_validate)
    if not files:
        raise EmptyDirectoryError

    if not os.path.isdir(path_to_validate):
        raise NotADirectoryError

    i_raw = 0
    i_meta = 0
    for filename in sorted(files, key=lambda x: int(re.match(r'\d+', x).group())):
        if re.fullmatch(r'\d+_raw.txt', filename):
            idx = int(re.match(r'\d+', filename).group())
            if idx != i_raw + 1:
                raise InconsistentDatasetError
            i_raw += 1
        elif re.fullmatch(r'\d+_meta.json', filename):
            idx = int(re.match(r'\d+', filename).group())
            if idx != i_meta + 1:
                raise InconsistentDatasetError
            i_meta += 1
    else:
        if i_raw != i_meta:
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
