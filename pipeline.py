"""
Pipeline for text processing implementation
"""
from pymystem3 import Mystem
from pathlib import Path
from typing import List
import re

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
        for file in path.glob('*_raw.txt'):
            a_id = str(file).split('/')[-1].split('_')[0]
            a_id = int(a_id)
            self._storage[a_id] = article.Article(url=None, article_id=a_id)


    def get_articles(self):
        """
        Returns storage params
        """
        return self._storage


corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
# corpus_manager._scan_dataset()



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
            # print(tokens)
            processed_txt = []
            for token in tokens:
                processed_txt.append(str(token))
            article.save_processed(' '.join(processed_txt))
            #print(processed_txt)



    def _process(self) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """

        mystem_a = Mystem()
        result = mystem_a.analyze(self.text)
        tokens = []
        for element in result:
            if element.get('analysis'):
                tok = MorphologicalToken(element['text'], element['analysis'][0]['lex'])
                tok.mystem_tags = element['analysis'][0]['gr']
                tokens.append(tok)

        return tokens



#pipeline = TextProcessingPipeline(corpus_manager)
#pipeline.run()


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


def main():
    print('Your code goes here')
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
