"""
Pipeline for text processing implementation
"""

from typing import List
from pathlib import Path
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
        self.pymorph_tags = ''

    def __str__(self):
        return f'{self.normalized_form}<{self.mystem_tags}>({self.pymorph_tags})'

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
        for file in path.iterdir():
            if str(file).endswith('raw.txt'):
                num = int(file.parts[-1][0])
                self._storage[num] = Article(url=None, article_id=num)

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
        self.text = ''


    def run(self):
        """
        Runs pipeline process scenario
        """
        for file in self.corpus_manager.get_articles().values():
            self.text = file.get_raw_text()
            morph_process = self._process()
            text = []
            for token in morph_process:
                text.append(str(token))
            file.save_processed(' '.join(text))

    def public_method(self):
        pass



    def _process(self) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        result = Mystem().analyze(self.text)
        morph_tokens = []
        for token in result:
            if token.get('analysis') and token.get('text'):
                if token.get('analysis')[0].get('lex') and token.get('analysis')[0].get('gr'):
                    morph = MorphologicalToken(token.get('text'), token.get('analysis')[0].get('lex'))
                    morph.mystem_tags = token.get('analysis')[0].get('gr')
                    morph.pymorph_tags = MorphAnalyzer().parse(morph.original_word[0].tag)
                    morph_tokens.append(morph)
        return morph_tokens


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    if not isinstance(path_to_validate, str):
        raise UnknownDatasetError
    path = Path(path_to_validate)
    if path.exists():
        if not path.is_dir():
            raise NotADirectoryError
        if not list(path.iterdir()):
            raise EmptyDirectoryError
        meta = 0
        text = 0
        for file in path.iterdir():
            if str(file).endswith('meta.json'):
                meta += 1
            if str(file).endswith('raw.txt'):
                text += 1
        if meta != text:
            raise InconsistentDatasetError
    else:
        raise FileNotFoundError


def main():
    print('Your code goes here')


if __name__ == "__main__":
    main()
    validate_dataset(ASSETS_PATH)
    corpus_manager_0 = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager_0)
    pipeline.run()
