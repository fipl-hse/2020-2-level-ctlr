"""
Pipeline for text processing implementation
"""

from pathlib import Path
from typing import List
from pymystem3 import Mystem
from pymorphy2 import MorphAnalyzer
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

    def public_method(self):
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
        path = Path(self.path_to_raw_txt_data)
        for file in path.rglob('*.txt'):
            ind = str(file).split('\\')[-1].split('_')[0]
            self._storage[ind] = Article(url=None, article_id=ind)

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

        for article in articles.values():
            self.raw_text = article.get_raw_text()
            tokens = self._process()
            processed_tokens = []
            for token in tokens:
                processed_tokens.append(str(token))
            article.save_processed(' '.join(processed_tokens))

    def _process(self) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        morph_analyzer = MorphAnalyzer()
        result = Mystem().analyze(self.raw_text)
        tokens = []

        for current_word in result:
            if current_word.get('analysis') and current_word.get('text'):
                if current_word['analysis'][0].get('lex') and current_word['analysis'][0].get('gr'):
                    morph_token = MorphologicalToken(current_word['text'], current_word['analysis'][0]['lex'])
                    morph_token.mystem_tags = current_word['analysis'][0]['gr']
                    morph_token.pymorphy_tags = morph_analyzer.parse(morph_token.original_word)[0].tag
                    tokens.append(morph_token)
        return tokens

    def public_method(self):
        pass


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
        raws = list(path.rglob('*_raw.txt'))
        if not raws:
            raise EmptyDirectoryError
        metas = list(path.rglob('*.json'))
        if len(raws) != len(metas):
            raise InconsistentDatasetError
    else:
        raise FileNotFoundError


def main():
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
