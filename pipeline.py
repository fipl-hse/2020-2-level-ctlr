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
    def __init__(self, normalized_form, original_word):
        self.original_word = original_word
        self.normalized_form = normalized_form
        self.mystem_tags = ''
        self.pymorphy_tags = ''

    def __str__(self):
        return f"{self.normalized_form}<{self.mystem_tags}>({self.pymorphy_tags})"

    def public_method(self):
        pass


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
        for file in Path(self.path_to_raw_txt_date).rglob('*_raw.txt'):
            id_each = int(file.parts[-1].split('_')[0])
            self._storage[id_each] = Article(url=None, article_id=id_each)

    def get_articles(self):
        """
        Returns storage params
        """
        return self._storage

    def public_method(self):
        pass


class TextProcessingPipeline:
    """
    Process articles from corpus manager
    """

    def __init__(self, corpus_manager: CorpusManager):
        self.corpus_manager = corpus_manager
        self.raw_text = ''

    def run(self):
        """
        Runs pipeline process scenario
        """
        for article in self.corpus_manager.get_articles().values():
            self.raw_text = article.get_raw_text()
            processed_text = list(map(str, self._process()))
            article.save_processed(' '.join(processed_text))

    def _process(self) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        process = Mystem().analyze(self.raw_text)
        tokens = []

        for tok in process:
            if tok.get('analysis') and tok.get('text'):
                morph_token = MorphologicalToken(original_word=tok['text'], normalized_form=tok['analysis'][0]['lex'])
                morph_token.mystem_tags = tok['analysis'][0]['gr']
                morph_token.pymorphy_tags = MorphAnalyzer().parse(word=morph_token.original_word)[0].tag
                tokens.append(morph_token)

        return tokens

    def public_method(self):
        pass


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
    validate_dataset(ASSETS_PATH)

    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)

    pipeline.run()


if __name__ == "__main__":
    # YOUR CODE HERE
    main()
