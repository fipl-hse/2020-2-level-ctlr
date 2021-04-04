"""
Pipeline for text processing implementation
"""

import os
import re
from pymystem3 import Mystem
from article import Article
from pathlib import Path
from typing import List
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
        return self.normalized_form


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
        files = os.listdir(self.path_to_raw_txt_data)
        for file in files:
            ind_underscore = file.index('_')
            raw_txt_is = re.match(r'.+_raw\.txt', file)
            if raw_txt_is:
                self._storage[int(file[:ind_underscore])] = Article(url=None, article_id=int(file[:ind_underscore]))
        return None

    def get_articles(self):
        """
        Returns storage params
        """
        self._scan_dataset()
        return self._storage.values()


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
        articles = self.corpus_manager.get_articles()
        for article in articles:
            self.article = article.get_raw_text()
            result = Mystem().analyze(article)
            tokens = self._process(mystem_analize_result=result)
            processed_text_tokens = []
            for token in tokens:
                processed_text_tokens.append('{}<{}>'.format(token.__str__(), token.mystem_tags))
            processed_text = ' '.join(processed_text_tokens)
            article.save_processed(processed_text)
        return None

    def _process(self, mystem_analize_result) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        tokens = []
        mystem = Mystem().analyze(self.article)
        for word in mystem:
            if word.get('analysis'):
                token = MorphologicalToken(word['text'], word['analysis'][0].get('lex'))
                token.mystem_tags = '{}'.format(word['analysis'][0].get('gr'))
                tokens.append(token)
        return tokens


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    path = Path(path_to_validate)

    if not isinstance(path_to_validate, str):
        raise UnknownDatasetError

    if path.exists():
        if not path.is_dir():
            raise NotADirectoryError

        if not list(path.iterdir()):
            raise EmptyDirectoryError
    else:
        raise FileNotFoundError

            
def main():
    print('Your code goes here')
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    pipeline.run()
    

if __name__ == "__main__":
    main()
