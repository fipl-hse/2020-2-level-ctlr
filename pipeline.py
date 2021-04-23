"""
Pipeline for text processing implementation
"""
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


class CorpusManager:
    """
    Works with articles and stores them
    """
    def __init__(self, path_to_raw_txt_data: str):
        self._storage = {}
        self.path_to_dataset = path_to_raw_txt_data

        self._scan_dataset()

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        path = Path(self.path_to_dataset)
        for file in path.rglob('*.txt'):
            i = int(file.parts[-1].split('_')[0])
            self._storage[i] = article.Article(url=None, article_id=i)

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
        self._text_to_process = ''

    def run(self):
        """
        Runs pipeline process scenario
        """
        articles = self.corpus_manager.get_articles()
        for file in articles.values():
            self._text_to_process = file.get_raw_text()
            morph_words = []
            for word in self._process():
                morph_words.append(str(word))
            file.save_processed(' '.join(morph_words))

    def _process(self) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        mystem_analyser = Mystem()
        pymorphy_analyser = MorphAnalyzer()
        result = mystem_analyser.analyze(self._text_to_process)
        morph_tokens = []
        for word in result:
            if word.get('analysis') and word.get('text'):
                if word['analysis'][0].get('lex') and word['analysis'][0].get('gr'):
                    morph_token = MorphologicalToken(word['text'], word['analysis'][0]['lex'])
                    morph_token.mystem_tags = word['analysis'][0]['gr']
                    morph_tokens.append(morph_token)
        for token in morph_tokens:
            tokens_pymorhy = pymorphy_analyser.parse(token.original_word)
            if tokens_pymorhy:
                token.pymorphy_tags = tokens_pymorhy[0].tag
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
        files = list(path.rglob('*_raw.txt'))
        if not files:
            raise EmptyDirectoryError
        ids = []
        for file in files:
            ids.append(int(file.parts[-1].split('_')[0]))
        if len(ids) != len(files) or not set(ids) == set(range(min(ids), max(ids) + 1)):
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
