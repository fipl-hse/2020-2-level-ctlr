"""
Pipeline for text processing implementation
"""
import os
import re
from pathlib import Path
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
        self.raw_text = ""

    def run(self):
        """
        Runs pipeline process scenario
        """
        articles = self.corpus_manager.get_articles()

        for article in articles.values():
            self.raw_text = article.get_raw_text()
            tokens = self._process()
            processed_text = []
            for token in tokens:
                processed_text.append(str(token))
            article.save_processed(' '.join(processed_text))

    def _process(self) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        process = Mystem().analyze(self.raw_text)
        tokens = []

        for token in process:
            if token.get('analysis') and token.get('text'):
                morph_token = MorphologicalToken(original_word=token['text'],
                                                 normalized_form=token['analysis'][0]['lex'])
                morph_token.mystem_tags = token['analysis'][0]['gr']
                tokens.append(morph_token)

        return tokens


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    path = Path(path_to_validate)

    if not path.exists():
        raise FileNotFoundError

    if not path.is_dir():
        raise NotADirectoryError

    if not list(path.iterdir()):
        raise EmptyDirectoryError


def main():
    print('Your code goes here')
    from constants import ASSETS_PATH

    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
