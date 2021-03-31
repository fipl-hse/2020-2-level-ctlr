"""
Pipeline for text processing implementation
"""

import os
import re
from typing import List

from pymystem3 import Mystem

from article import Article
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
        return f"{self.normalized_form}<{self.mystem_tags}>"


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
        for i in range(len(os.listdir(self.path_to_raw_txt_data)) // 2):
            self._storage[i] = Article(url=None, article_id=i)

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
        self._current_article_id = 0  # todo ?
        self._currant_article = ''

    def run(self):
        """
        Runs pipeline process scenario
        """
        articles = self.corpus_manager.get_articles()
        for article in articles.values():
            article.text = article.get_raw_text()
            self._current_article_id = article.article_id  # todo ?
            self._currant_article = article.text
            tokens = self._process()
            tokens = ' '.join([str(token) for token in tokens])
            article.save_processed(tokens)

    def _process(self) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        text = self._currant_article
        # text = self.corpus_manager.get_articles()[self._current_article_id] todo ?

        # text = re.sub('ºС', ' градусов', text)
        text = ' '.join(re.findall(r'\w+', text.lower()))
        result = Mystem().analyze(text)
        tokenized_text = []

        for word in result[::2]:  # skip whitespaces
            original = word['text']
            if re.fullmatch(r'\d+', original):  # catch digits
                normalized = word['text']
                tags = 'NUM='

            else:
                try:
                    normalized = word['analysis'][0]['lex']
                except (KeyError, IndexError):
                    continue
                tags = word['analysis'][0]['gr']

            token = MorphologicalToken(original, normalized)
            token.mystem_tags = tags
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

    if len(files) % 2:  # odd number of files
        raise InconsistentDatasetError

    files_number = len(files) // 2
    for i in range(files_number):
        if not (os.path.exists(os.path.join(path_to_validate, f'{i}_meta.json'))
                or os.path.exists(os.path.join(path_to_validate, f'{i}_raw.txt'))):
            raise InconsistentDatasetError


def main():
    validate_dataset(ASSETS_PATH)

    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    pipeline.run()

    # token = MorphologicalToken(original_word, normalized_form)


if __name__ == "__main__":
    main()
