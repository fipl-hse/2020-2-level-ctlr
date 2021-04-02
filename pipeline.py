"""
Pipeline for text processing implementation
"""

import os
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
        return '{}<{}>{}'.format(str(self.normalized_form), str(self.mystem_tags), str(self.pymorphy_tags))


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
        articles_for_store = []
        all_files = os.listdir(self.path_to_raw_txt_data)
        for file in all_files:
            if file == r'..raw.txt':
                articles_for_store.append(file)
        for article in articles_for_store:
            article_id = article.split('_')[0]
            self._storage[article_id] = Article(url=None, article_id=article_id)

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
        article_storage = self.corpus_manager.get_articles()
        for article in article_storage.values():
            self.raw_text = article.get_raw_text()
            final_tokens = self._process()
            final_info = []
            for token in final_tokens:
                final_info.append(token.__str__())
            article.save_processed(' '.join(final_info))

    def _process(self) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        mystem_tool = Mystem()
        morphy_tool = pymorphy2.MorphAnalyzer()
        result = mystem_tool.analyze(self.raw_text)
        tokens = []
        for word in result:
            if word["analysis"]:
                token = MorphologicalToken(original_word=word["text"], normalized_form=word["analysis"][0]["lex"])
                token.mystem_tags = word["analysis"][0]["gr"]
                tokens.append(token)
        for token in tokens:
            token.pymorphy_tags = morphy_tool.parse(token.original_word)[0].tag
        return tokens


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    check_files = True
    check_consistency = True

    if not os.path.exists(path_to_validate):
        raise FileNotFoundError

    if not os.path.isdir(path_to_validate):
        raise NotADirectoryError

    consistency = os.listdir(path_to_validate)
    if not consistency:
        check_files = False

    if not check_files:
        raise EmptyDirectoryError

    id_meta = []
    id_article = []
    for file in consistency:
        if file == '*.json':
            id_meta.append(file.split('_')[0])
        elif file == '*._raw.txt':
            id_article.append(file.split('_')[0])
    if set(id_meta) != set(id_article):
        check_consistency = False

    if not check_consistency:
        raise InconsistentDatasetError

    if check_files and check_consistency:
        return None


def main():
    print('Your code goes here')
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
