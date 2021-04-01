"""
Pipeline for text processing implementation
"""

import os
from pathlib import Path
from typing import List
from pymorphy2 import MorphAnalyzer
from pymystem3 import Mystem
import article
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
        return "{}<{}>({})".format(self.normalized_form, self.mystem_tags, self.pymorphy_tags)

    def public_method(self):
        pass


class CorpusManager:
    """
    Works with articles and stores them
    """
    def __init__(self, path_to_raw_txt_data: str):
        self.path_to_data = path_to_raw_txt_data
        self._storage = {}

        self._scan_dataset()

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        for one_file in Path(self.path_to_data).rglob('*_raw.text'):
            key_number = int(one_file.name.split('_')[0])
            self._storage[key_number] = article.Article(url=None, article_id=key_number)

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
        for one_article in articles.values():
            self.raw_text = one_article.get_raw_text()
            tokens = self._process()
            one_article.save_processed(' '.join(tokens))

    def _process(self) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        result = Mystem().analyze(self.raw_text)
        tokens = []
        for analyzed_word in result:
            if analyzed_word.get('analysis'):  # чтобы были только слова
                token = MorphologicalToken(original_word=analyzed_word['text'],
                                           normalized_form=analyzed_word['analysis'][0]['lex'])
                token.mystem_tags = analyzed_word['analysis'][0]['gr']
                token.pymorphy_tags = MorphAnalyzer().parse(word=token.original_word)[0].tag
                tokens.append(str(token))
        return tokens

    def public_method(self):
        pass


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    if not os.path.exists(path_to_validate):
        raise FileNotFoundError

    if not isinstance(path_to_validate, str):
        raise UnknownDatasetError

    if os.path.exists(path_to_validate):

        if not Path(path_to_validate).is_dir():
            raise NotADirectoryError

        dir_content = os.listdir(path_to_validate)
        if not dir_content:
            raise EmptyDirectoryError

        files = []
        files_ids = []
        for one_file in dir_content:
            if '_raw.txt' in str(one_file):
                files.append(one_file)
                files_ids.append(int(str(one_file)[0]))
        if len(files) != len(files_ids) or set(files_ids) != set(range(1, len(files) + 1)):
            raise InconsistentDatasetError


def main():
    print('Your code goes here')
    validate_dataset(ASSETS_PATH)  # step 1
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)  # step 2
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)  # step 4
    pipeline.run()


if __name__ == "__main__":
    main()
