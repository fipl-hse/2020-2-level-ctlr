"""
Pipeline for text processing implementation
"""
import os
from typing import List
from pymystem3 import Mystem
from pymorphy2 import MorphAnalyzer
from constants import ASSETS_PATH
from article import Article


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
        return '{normalized_form}<{mystem}>({pymorphy})'.format(normalized_form=self.normalized_form,
                                                                mystem=self.mystem_tags,
                                                                pymorphy=self.pymorphy_tags)

    def some_public_method(self):
        pass


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
        for filename in os.listdir(self.path_to_raw_txt_data):
            if filename.endswith('_raw.txt'):
                underscore_idx = filename.index('_')
                article_id = int(filename[:underscore_idx])
                self._storage[article_id] = Article(url=None, article_id=article_id)

    def get_articles(self):
        """
        Returns storage params
        """
        return self._storage

    def some_public_method(self):
        pass


class TextProcessingPipeline:
    """
    Process articles from corpus manager
    """
    def __init__(self, corpus_manager: CorpusManager):
        self.corpus_manager = corpus_manager
        self.raw_text_article = ''

    def run(self):
        """
        Runs pipeline process scenario
        """
        for article in self.corpus_manager.get_articles().values():
            self.raw_text_article = article.get_raw_text()
            tokens = self._process
            article.save_processed(' '.join(tokens))

    def _process(self) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        morph_analysis_res = Mystem().analyze(self.raw_text_article)
        # res_ex: {"text":"светится","analysis":[{"lex":"светиться","gr":"V,несов,нп=непрош,ед,изъяв,3-л"}]}
        morph_tokens = []
        for word in morph_analysis_res:
            if word.get('analysis'):
                token = MorphologicalToken(original_word=word['text'], normalized_form=word['analysis'][0]['lex'])
                token.mystem_tags = word['analysis'][0]['gr']
                token.pymorphy_tags = MorphAnalyzer().parse(token.original_word)[0].tag
                morph_tokens.append(str(token))
        return morph_tokens

    def some_public_method(self):
        pass


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


def main():
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
