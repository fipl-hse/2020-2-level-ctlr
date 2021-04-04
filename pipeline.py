"""
Pipeline for text processing implementation
"""

from typing import List
from constants import ASSETS_PATH
from pathlib import Path
from article import Article

from pymystem3 import Mystem


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

    def __str__(self):
        return f"{self.normalized_form}<{self.mystem_tags}>"


class CorpusManager: #для чтения
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

        for one_file in path.glob('*_raw.txt'):
            idx = str(one_file).split('/')[-1].split('_')[0]
            self._storage[idx] = Article(url=None, article_id=idx)

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
        articles = self.corpus_manager.get_articles()
        for raw in articles.values():
            self.text = raw.get_raw_text()
            text = self._process()
            raw.save_processed(' '.join(map(str, text)))

    def _process(self) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        mystem = Mystem().analyze(self.text)
        tokens = []

        for word in mystem:
            if word.get('analysis'):
                token = MorphologicalToken(word['text'], word['analysis'][0]['lex'])
                token.mystem_tags = word['analysis'][0]['gr']
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
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
