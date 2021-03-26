"""
Pipeline for text processing implementation
"""
import os
from typing import List

from pymorphy2 import MorphAnalyzer
from pymystem3 import Mystem

from article import Article
from constants import ASSETS_PATH
from pos_frequency_pipeline import POSFrequencyPipeline


class EmptyDirectoryError(Exception):
    """
    Custom error
    """


# class NotADirectoryError(Exception):
#     """
#     Custom error
#     """


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
        self.original = original_word
        self.normalized = normalized_form
        self.mystem_tags = ''
        self.pymorphy_tags = ''

    def __str__(self):
        return self.normalized + '<' + self.mystem_tags + '>' + '(' + str(self.pymorphy_tags) + ')'

    def placeholder_public_method(self):
        """
        In order to pass lint check,
        class must contain at least
        two public methods
        """
        pass


class CorpusManager:
    """
    Works with articles and stores them
    """
    def __init__(self, path_to_raw_txt_data: str):
        self.path_to_raw = path_to_raw_txt_data
        self._storage = {}

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        for file in os.listdir(ASSETS_PATH):
            if file.endswith('_raw.txt'):
                index = file.split('_raw.txt')[0]
                self._storage[index] = Article(url=None, article_id=index)

    def get_articles(self):
        """
        Returns storage params
        """
        self._scan_dataset()
        return self._storage

    def placeholder_public_method(self):
        """
        In order to pass lint check,
        class must contain at least
        two public methods
        """
        pass


class TextProcessingPipeline:
    """
    Process articles from corpus manager
    """
    def __init__(self, corpus_manager: CorpusManager):
        self.corpus = corpus_manager

    def run(self):
        """
        Runs pipeline process scenario
        """
        print(f'there are {len(self.corpus.get_articles())} articles to process')
        for article in self.corpus.get_articles().values():
            raw_text = article.get_raw_text()
            tokens = self._process(raw_text)
            processed = ' '.join(map(str, tokens))
            article.save_processed(processed)

    def placeholder_public_method(self):
        """
        In order to pass lint check,
        class must contain at least
        two public methods
        """
        pass

    @staticmethod
    def _process(text) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        mystem = Mystem()
        pymorphy = MorphAnalyzer()
        words = mystem.analyze(text)
        tokens = []
        for word in words:
            orig = word['text'].strip()
            if orig.isalpha():
                try:
                    token = MorphologicalToken(original_word=orig, normalized_form=word['analysis'][0]['lex'])
                    token.mystem_tags = word['analysis'][0]['gr'].strip()
                    token.pymorphy_tags = pymorphy.parse(orig)[0].tag
                    tokens.append(token)
                except IndexError:
                    token = MorphologicalToken(original_word=orig, normalized_form=orig)
                    tokens.append(token)
        return tokens


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    if not os.path.exists(path_to_validate):
        raise FileNotFoundError
    if not os.path.isdir(path_to_validate):
        raise NotADirectoryError
    if not os.listdir(path_to_validate):
        raise EmptyDirectoryError
    metas, raws = 0, 0
    for file in os.listdir(ASSETS_PATH):
        if file.endswith("_raw.txt"):
            raws += 1
        if file.endswith("_meta.json"):
            metas += 1
    if not metas == raws:
        raise InconsistentDatasetError


def main():
    validate_dataset(ASSETS_PATH)
    print('validated dataset')
    corpus_manager = CorpusManager(ASSETS_PATH)
    print('onto processing')
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    pipeline.run()
    print('onto analytics')
    visualizer = POSFrequencyPipeline(corpus_manager)
    visualizer.run()


if __name__ == "__main__":
    main()
