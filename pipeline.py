# pylint: disable=R0903
"""
Pipeline for text processing implementation
"""

from pathlib import Path
from typing import List

import pymorphy2
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
        return self.normalized_form + f'<{self.mystem_tags}>' + f'({self.pymorphy_tags})'


class CorpusManager:
    """
    Works with articles and stores them
    """
    def __init__(self, path_to_dataset: str):
        self.path_to_raw_txt_data = path_to_dataset
        self._storage = self._scan_dataset()

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        path = Path(self.path_to_raw_txt_data)
        all_files = [str(f_path) for f_path in path.iterdir()]
        raw_files = {}

        for file in all_files:
            if '_raw.txt' in file:
                text_id = int(file.split('\\')[-1].split('_')[0])
                raw_files[text_id] = Article(url=None, article_id=text_id)

        return raw_files

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

        storage = self.corpus_manager.get_articles()

        for article_id, article in storage.items():
            self._text = article
            processed_text = list(map(str, self._process()))
            article.save_processed(' '.join(processed_text))

    def _process(self) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        text = self._text.get_raw_text()
        result = Mystem().analyze(text)
        tokens = []

        for word in result:

            if 'analysis' in word and word['analysis']:
                token = MorphologicalToken(original_word=word, normalized_form=word['analysis'][0]['lex'])
                token.mystem_tags = word['analysis'][0]['gr']

                morph = pymorphy2.MorphAnalyzer()
                pymorphy_tags = morph.parse(word['text'])
                token.pymorphy_tags = pymorphy_tags[0].tag

                tokens.append(token)

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

    if len(list(path.iterdir())) % 2:
        raise InconsistentDatasetError


def main():
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(path_to_dataset=ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
