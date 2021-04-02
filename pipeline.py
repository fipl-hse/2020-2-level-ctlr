"""
Pipeline for text processing implementation
"""
import re
from collections import namedtuple
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
            article_id = int(re.match(r"^\d+", idx.parts[-1]).group())
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
    text: str

    def __init__(self, corpus_manager: CorpusManager):
        self.corpus_manager = corpus_manager

    def run(self):
        """
        Runs pipeline process scenario
        """
        for article in self.corpus_manager.get_articles().values():
            self.text = article.get_raw_text()
            processed_text = self._process()
            article.save_processed(" ".join(map(str, processed_text)))

    def _process(self) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        result = Mystem().analyze(self.text)
        morph = MorphAnalyzer()
        word_filter = re.compile(r"[^\w-]+")

        processed_text: List[MorphologicalToken] = []

        for token in result:

            if token.get("analysis") and token.get("text"):
                if token["analysis"][0].get("lex"):
                    morph_token = MorphologicalToken(
                        word_filter.sub("", token["text"]),
                        word_filter.sub("", token["analysis"][0]["lex"])
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
    Check = namedtuple("Check", ["status", "error"])

    paths = tuple(path.glob("*_raw.txt")), tuple(path.glob("*_meta.json"))
    sorted_paths = [
        sorted(arr, key=lambda x: int(re.match(r"^\d+", x.name).group()))
        for arr in paths
    ]
    valid_order = [str(x) for x in range(1, max(len(paths[0]), len(paths[1])) + 1)]

    is_num_raw_meta_equal = len(paths[0]) == len(paths[1])
    are_nums_consequent = list(
        all(x.name.startswith(n) for x in p)
        for *p, n in zip(*sorted_paths, valid_order)
    )

    checks = (
        Check(path.is_dir(), NotADirectoryError),
        Check(path.exists(), FileNotFoundError),
        Check(any(path.iterdir()), EmptyDirectoryError),
        Check(
            is_num_raw_meta_equal or all(are_nums_consequent), InconsistentDatasetError
        ),
    )

    for check in checks:
        if not check.status:
            raise check.error("Error occurred while checking config.")


def main():
    validate_dataset(ASSETS_PATH)

    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)

    pipeline.run()


if __name__ == "__main__":
    main()
