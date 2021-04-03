"""
Pipeline for text processing implementation
"""
from pathlib import Path
import re
from typing import List
from pymystem3 import Mystem
from pymorphy2 import MorphAnalyzer
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

class MorphologicalToken: # pylint: disable=too-few-public-methods
    """
    Stores language params for each processed token
    """
    def __init__(self, original_word, normalized_form):
        self.original_word = original_word
        self.normalized_form = normalized_form
        self.mystem_tags = ""
        self.pymorthy_tags = ""

    def __str__(self):
        return f"{self.normalized_form}<{self.mystem_tags}>({self.pymorthy_tags})"


class CorpusManager: # pylint: disable=too-few-public-methods
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
        files_txt = [str(file.name) for file in Path(self.path_to_raw_txt_data).glob('**/*.txt')]
        for file in files_txt:
            file_ind = file[0]
            self._storage[file_ind] = Article(None, file_ind)

    def get_articles(self):
        """
        Returns storage params
        """
        self._scan_dataset()
        return self._storage


class TextProcessingPipeline: # pylint: disable=too-few-public-methods
    """
    Process articles from corpus manager
    """
    def __init__(self, corpus_manager: CorpusManager):
        self.corpus_manager = corpus_manager

    def run(self):
        """
        Runs pipeline process scenario
        """
        articles = self.corpus_manager.get_articles()  # dict with key - num, value - article instance
        for article in articles.values():
            raw_text = article.get_raw_text()
            tokens = [i.__str__() for i in  self._process(raw_text)]
            article.save_processed(" ".join(tokens))
    @classmethod
    def _process(cls, raw_text) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        text = re.sub(r"[^a-zа-я\s]","", raw_text.lower())
        raw_tokens = Mystem().analyze(text)
        morphological_tokens = []
        for word in raw_tokens:
            if word["text"].isalpha() and word["analysis"]:
                morph_token = MorphologicalToken(word["text"], word["analysis"][0]["lex"])
                morph_token.mystem_tags = word["analysis"][0]["gr"]
                morph_token.pymorthy_tags = str(MorphAnalyzer().parse(word["text"])[0].tag)

                morphological_tokens.append(morph_token)
        return morphological_tokens


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    path = Path(path_to_validate)
    if not path.exists():
        raise FileNotFoundError
    if not path.is_dir():
        raise NotADirectoryError
    checks = list(path.glob('**/*.txt'))
    if not checks:
        raise EmptyDirectoryError

def main():
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager)
    pipeline.run()

if __name__ == "__main__":
    main()
