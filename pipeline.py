"""
Pipeline for text processing implementation
"""
import os

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
        return str(self.normalized_form) + '<' + str(self.mystem_tags) + '>' + '(' + str(self.pymorphy_tags) + ')'

    def public_method(self):
        pass


class CorpusManager:
    """
    Works with articles and stores them
    """
    def __init__(self, path_to_raw_txt_data: str):
        self.data_path = path_to_raw_txt_data
        self._storage = {}

        self._scan_dataset()

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        path = Path(self.data_path)
        for file in path.rglob('*.txt'):
            number = int(file.parts[-1].split('_')[0])
            self._storage[number] = Article(url=None, article_id=number)

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
        articles = self.corpus_manager.get_articles()
        for article in articles.values():
            self.raw_text = article.get_raw_text()
            list_of_tokens = self._process()
            list_of_strs = []
            for token in list_of_tokens:
                list_of_strs.append(token.__str__())
            article.save_processed(' '.join(list_of_strs))

    def _process(self) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        result = Mystem().analyze(self.raw_text)
        morph_analyzer = MorphAnalyzer()
        list_of_tokens = []
        for stem_dict in result:
            if stem_dict.get('analysis'):
                original_word = stem_dict['text']
                normalized_form = stem_dict['analysis'][0]['lex']
                token = MorphologicalToken(original_word, normalized_form)
                token.mystem_tags = stem_dict['analysis'][0]['gr']
                token.pymorphy_tags = morph_analyzer.parse(stem_dict['text'])[0].tag
                list_of_tokens.append(token)
        return list_of_tokens

    def public_method(self):
        pass


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    if not path_to_validate:
        raise UnknownDatasetError

    if not os.path.exists(path_to_validate):
        raise FileNotFoundError

    if not os.path.isdir(path_to_validate):
        raise NotADirectoryError

    metas, raws = 0, 0
    for file in os.listdir(ASSETS_PATH):
        if file.endswith("_raw.txt"):
            raws += 1
        if file.endswith("_meta.json"):
            metas += 1
    if raws != metas:
        raise InconsistentDatasetError

    if not os.listdir(path_to_validate):
        raise EmptyDirectoryError


def main():
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
