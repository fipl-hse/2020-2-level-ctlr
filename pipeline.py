"""
Pipeline for text processing implementation
"""
import os
from typing import List
from pathlib import Path
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
        self.pymystem_tags = ''
        self.pymorphy_tags = ''

    def __str__(self):
        return "{}<{}>({})".format(self.normalized_form, self.pymystem_tags, self.pymorphy_tags)
    def get_sth(self):
        pass


class CorpusManager:
    """
    Works with articles and stores them
    """
    def __init__(self, path_to_raw_txt_data: str):
        self._storage={}
        self.path_to_dataset = path_to_raw_txt_data
        self._scan_dataset()



    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        path = Path(self.path_to_dataset)
        for file  in path.glob('*_raw.txt'):
            ind = int(file.parts[-1].split('_')[0])
            self._storage[ind] = Article(url=None, article_id=ind)
        self._storage[ind] = Article(url=None, article_id=ind)

    def get_articles(self):
        """
        Returns storage params
        """
        return self._storage

    def get_sth(self):
        pass

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
        articles = self.corpus_manager.get_articles()
        for article in articles.values():
            self.text = article.get_raw_text()
            m_tokens = self._process()
            processed_text = []
            for tok in m_tokens:
                processed_text.append(str(tok))
            article.save_processed(' '.join(processed_text))

    def _process(self) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        result=Mystem().analyze(self.text)
        m_tokens=[]
        for tok in result:
            m_token = MorphologicalToken(tok['text'], tok['analysis'][0]['lex'])
            m_token.pymystem_tags = tok['analysis'][0]['gr']
            m_token.pymorphy_tags = MorphAnalyzer().parse(m_token.original_word)[0].tag
            m_tokens.append(m_token)
        return m_tokens

    def get_sth(self):
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
    print('Your code goes here')
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    pipeline.run()

if __name__ == "__main__":
    main()
