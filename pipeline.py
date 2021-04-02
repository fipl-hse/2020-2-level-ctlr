"""
Pipeline for text processing implementation
"""
from pymorphy2 import MorphAnalyzer
from pymystem3 import Mystem
from typing import List
from pathlib import Path
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
    def __init__(self, normalized_form, original_word):
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
        for file in Path(self.path_to_raw_txt_date).rglob('*_raw.txt'):
            id = str(file).split('\\')[-1].split('_')[0]
            self._storage[id] = Article(url=None, article_id=id)

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
        for article in self.corpus_manager.get_articles().values():
            self.raw_text = article.get_raw_text()
            processed_text = list(map(str, self._process()))
            article.save_processed(' '.join(processed_text))

    def _process(self) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        result = Mystem().analyze(self.raw_text)
        tokens = []

        for word in result:
            try:
                token = MorphologicalToken(original_word=word['text'], normalized_form=word['analysis'][0]['lex'])
                token.mystem_tags = word['analysis'][0]['gr']
                tokens.append(token)
            except (IndexError, KeyError):
                if not word['text'].isnumeric():
                    continue
            for token in tokens:
                token.pymorphy_tags = MorphAnalyzer().parse(token.original_word)[0].tag

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


def main():
    validate_dataset(ASSETS_PATH)

    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)

    pipeline.run()


if __name__ == "__main__":
    # YOUR CODE HERE
    main()
