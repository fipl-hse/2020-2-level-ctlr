"""
Pipeline for text processing implementation
"""
import os
import re
from pymystem3 import Mystem
from pymorphy2 import MorphAnalyzer
from typing import List
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
        self.pymorthy_tags = ""

    def __str__(self):
        return f"{self.normalized_form}<{self.mystem_tags}>({self.pymorthy_tags})"


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
        files_txt = [file for file in os.listdir(self.path_to_raw_txt_data) if file.endswith(".txt")]
        for file in files_txt:
            file_ind = file[0]
            self._storage[file_ind] = Article(None, file_ind)

    def get_articles(self):
        """
        Returns storage params
        """
        self._scan_dataset()
        return self._storage


class TextProcessingPipeline:
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
        for art_num, article in articles.items():
            raw_text = article.get_raw_text()
            tokens = [i.__str__() for i in  self._process(raw_text)]
            article.save_processed(" ".join(tokens))

    def _process(self, raw_text) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        text = re.sub(r"[^a-zа-я\s]","", raw_text.lower())
        raw_tokens = Mystem().analyze(text)
        morphological_tokens = []
        for word in raw_tokens:
            if word["text"].isalpha():
                morph_token = MorphologicalToken(word["text"], word["analysis"][0]["lex"])
                morph_token.mystem_tags = word["analysis"][0]["gr"]
                morph_token.pymorthy_tags = str(MorphAnalyzer().parse(word["analysis"][0]["lex"])[0].tag)

                morphological_tokens.append(morph_token)
        return morphological_tokens


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    if not os.path.isdir(path_to_validate):
        raise UnknownDatasetError
    files_dir = os.listdir(path_to_validate)
    if not files_dir:
        raise EmptyDirectoryError

    checks = [p_name.endswith(".txt") or p_name.endswith(".json") for p_name in files_dir]
    if not all(checks):
        raise InconsistentDatasetError

def main():
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager)
    pipeline.run()

if __name__ == "__main__":
    main()
