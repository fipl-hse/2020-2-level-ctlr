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
        self.mystem_tags = ""
        self.pymorphy_tags = ""

    def __str__(self):
        return f"{self.normalized_form}<{self.mystem_tags}>({self.pymorphy_tags})"

    def sample(self):
        raise NotImplementedError


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
        path = Path(self.path_to_raw_txt_data)

        for idx in path.glob(r"*_raw.txt"):
            article_id = re.match(r"^\d+", idx.parts[-1]).group()
            self._storage[article_id] = Article(url=None, article_id=article_id)

    def get_articles(self):
        """
        Returns storage params
        """
        return self._storage

    def sample(self):
        raise NotImplementedError


class TextProcessingPipeline:
    """
    Process articles from corpus manager
    """

    def __init__(self, corpus_manager: CorpusManager):
        self.corpus_manager = corpus_manager
        self.text = ""

    def run(self):
        """
        Runs pipeline process scenario
        """
        for idx in self.corpus_manager.get_articles():
            article = Article(url=None, article_id=idx)
            self.text = article.get_raw_text()
            processed_text = self._process()
            article.save_processed(" ".join(map(str, processed_text)))

    def sample(self):
        raise NotImplementedError

    def _process(self) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        result = Mystem().analyze(self.text)
        morph = MorphAnalyzer()

        processed_text: List[MorphologicalToken] = []

        for token in result:

            if token.get("analysis"):
                morph_token = MorphologicalToken(
                    token["text"], token["analysis"][0]["lex"]
                )
                morph_token.mystem_tags = token["analysis"][0]["gr"]
                morph_token.pymorphy_tags = morph.parse(token["text"])[0].tag
                processed_text.append(morph_token)

        return processed_text


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    path = Path(path_to_validate)

    if not path.is_dir():
        raise NotADirectoryError

    if not any(path.iterdir()):
        raise EmptyDirectoryError


def main():
    validate_dataset(ASSETS_PATH)

    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)

    pipeline.run()


if __name__ == "__main__":
    main()
