"""
Pipeline for text processing implementation
"""

from pathlib import Path
from typing import List

from pymorphy2 import MorphAnalyzer
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
        self.pymorphy_tags = ''

    def __str__(self):
        return f"{self.normalized_form}<{self.mystem_tags}>({self.pymorphy_tags})"


class CorpusManager:
    """
    Works with articles and stores them
    """
    def __init__(self, path_to_raw_txt_data: str):
        self.path_to_raw_txt_date = path_to_raw_txt_data
        self._storage = {}
        self._scan_dataset()

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        path = Path(self.path_to_raw_txt_date)
        for file in path.rglob('*.txt'):
            article_id = int(file.name.split('_')[0])
            self._storage[article_id] = Article(url=None, article_id=article_id)

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
        for file in self.corpus_manager.get_articles().values():
            self._text = file.get_raw_text()
            tokens = self._process()
            file.save_processed(' '.join(map(str, tokens)))

    def _process(self) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        result = Mystem().analyze(self._text)
        tokens = []

        for token in result:
            if token.get('analysis') and token.get('text'):
                morph_token = MorphologicalToken(original_word=token['text'],
                                                 normalized_form=token['analysis'][0]['lex'])
                morph_token.mystem_tags = token['analysis'][0]['gr']
                morph_token.pymorphy_tags = MorphAnalyzer().parse(word=morph_token.original_word)[0].tag
                tokens.append(str(morph_token))

        return tokens


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    if not isinstance(path_to_validate, str):
        raise UnknownDatasetError
    path = Path(path_to_validate)
    if not path.exists():
        raise FileNotFoundError
    if not path.is_dir():
        raise NotADirectoryError
    if not list(path.iterdir()):
        raise EmptyDirectoryError

    # InconsistentDatasetError


def main():
    validate_dataset(ASSETS_PATH)

    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
