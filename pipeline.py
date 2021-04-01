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
        for element in path.glob('*_raw.txt'):
            index = int(element.parts[-1].split('_')[0])
            self._storage[index] = Article(url=None, article_id=index)

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
        for article in self.corpus_manager.get_articles().values():
            self.text = article.get_raw_text()
            tokens = self._process()
            article.save_processed(' '.join(map(str, tokens)))

    def _process(self) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        mystem_analyser = Mystem()
        pymotphy_analyser = MorphAnalyzer()
        result = mystem_analyser.analyze(self.text)
        morph_tokens = []
        for element in result:
            if element.get('analysis'):
                morph_token = MorphologicalToken(element['text'], element['analysis'][0]['lex'])
                morph_token.mystem_tags = element['analysis'][0]['gr']
                morph_tokens.append(morph_token)
        for token in morph_tokens:
            token_pymorhy = pymotphy_analyser.parse(token.original_word)[0]
            token.pymorphy_tags = token_pymorhy.tag
        return morph_tokens


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    pass


def main():
    print('Your code goes here')


if __name__ == "__main__":
    main()
