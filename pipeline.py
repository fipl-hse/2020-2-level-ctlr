# pylint: disable=R0903
"""
Pipeline for text processing implementation
"""

from pathlib import Path
from typing import List

from pymorphy2 import MorphAnalyzer
from pymystem3 import Mystem

import article
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
        self.pymorphy_tags = ''

    def __str__(self):
        return f"{self.normalized_form}<{self.mystem_tags}>({self.pymorphy_tags})"


class CorpusManager:
    """
    Works with articles and stores them
    """
    def __init__(self, path_to_raw_txt_data: str):
        self.path_to_raw_data = path_to_raw_txt_data
        self._storage = {}

        self._scan_dataset()

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        path = Path(self.path_to_raw_data)
        for file in path.rglob('*.txt'):
            ind = int(file.name.split('_')[0])
            self._storage[ind] = article.Article(url=None, article_id=ind)

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
        self.text = ''

    def run(self):
        """
        Runs pipeline process scenario
        """
        articles = self.corpus_manager.get_articles()
        for proc_article in articles.values():
            self.text = proc_article.get_raw_text()
            tokens = self._process()
            proc_article.save_processed(' '.join(map(str, tokens)))

    def _process(self) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        pymorphy = MorphAnalyzer()
        result = Mystem().analyze(self.text)
        tokens = []
        for token in result:
            if token.get('analysis') and token.get('text'):
                if token['analysis'][0].get('lex') and token['analysis'][0].get('gr'):
                    morph_token = MorphologicalToken(token['text'], token['analysis'][0]['lex'])
                    morph_token.mystem_tags = token['analysis'][0]['gr']
                    morph_token.pymorphy_tags = pymorphy.parse(morph_token.original_word)[0].tag
                    tokens.append(morph_token)
        return tokens


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    checked_path = Path(path_to_validate)
    if not checked_path.exists():
        raise FileNotFoundError

    if not checked_path.is_dir():
        raise NotADirectoryError

    if not list(checked_path.iterdir()):
        raise EmptyDirectoryError

    raw_files = list(checked_path.rglob('*.txt'))
    meta_files = list(checked_path.rglob('*.json'))
    raw_numbers = list(map(lambda file: int(file.name.split('_')[0]), raw_files))
    indexes = [i for i in range(min(raw_numbers), max(raw_numbers) + 1)]
    if len(raw_files) != len(meta_files) or sorted(raw_numbers) != indexes:
        raise InconsistentDatasetError


def main():
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
