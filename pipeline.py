"""
Pipeline for text processing implementation
"""

import os
from pathlib import Path, PurePath
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
        return f'{self.normalized_form}<{self.mystem_tags}>({self.pymorphy_tags})'


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
        raw_matches_paths = Path(self.path_to_raw_txt_data).rglob('*.txt')
        for raw_file_path in raw_matches_paths:
            id_article = PurePath(str(raw_file_path)).name.split('_')[0]
            self._storage[id_article] = Article(url=None, article_id=id_article)

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
        self.raw_text = ''

    def run(self):
        """
        Runs pipeline process scenario
        """
        for article in self.corpus_manager.get_articles().values():
            self.raw_text = article.get_raw_text()
            tokens = self._process()
            processed_tokens = list(map(str, tokens))
            article.save_processed(' '.join(processed_tokens))

    def _process(self) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        mystem_analyzer = Mystem()
        morphy_analyzer = MorphAnalyzer()
        result = mystem_analyzer.analyze(self.raw_text)
        tokens = []
        for analyzed_word in result:
            if 'analysis' in analyzed_word and analyzed_word['analysis']:
                token = MorphologicalToken(original_word=analyzed_word['text'],
                                           normalized_form=analyzed_word['analysis'][0]['lex'])
                token.mystem_tags = analyzed_word['analysis'][0]['gr']
                tokens.append(token)
        for token in tokens:
            token.pymorphy_tags = morphy_analyzer.parse(token.original_word)[0].tag

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
    if not os.listdir(path_to_validate):
        raise EmptyDirectoryError


def main():
    print('Your code goes here')
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
