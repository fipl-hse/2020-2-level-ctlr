"""
Pipeline for text processing implementation
"""
from pathlib import Path
from typing import List

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
        self.mystem_tags = ''
        self.pymorphy_tags = ''

    def __str__(self):
        return f'{self.normalized_form}<{self.mystem_tags}>({self.pymorphy_tags})'


class CorpusManager:
    """
    Works with articles and stores them
    """
    def __init__(self, path_to_raw_txt_data: str):
        self.data_path = path_to_raw_txt_data
        self._storage = {}

        self._scan_dataset()

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        path = Path(self.data_path)
        for file in path.rglob('*.txt'):
            idx = int(file.parts[-1].split('_')[0])
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
        self.raw_text = ''

    def run(self):
        """
        Runs pipeline process scenario
        """
        articles = self.corpus_manager.get_articles()
        for article in articles.values():
            self.raw_text = article.get_raw_text()
            list_of_tokens = self._process()
            article.save_processed(' '.join(map(str, list_of_tokens)))

    def _process(self) -> List[type(MorphologicalToken)]:
        """
        Performs processing of each text
        """
        result = Mystem().analyze(self.raw_text)
        morph_analyzer = MorphAnalyzer()
        list_of_tokens = []
        for stem_dict in result:
            if stem_dict.get('analysis') and stem_dict.get('text'):
                if stem_dict['analysis'][0].get('lex') and stem_dict['analysis'][0].get('gr'):
                    original_word = stem_dict['text']
                    normalized_form = stem_dict['analysis'][0]['lex']
                    token = MorphologicalToken(original_word, normalized_form)
                    token.mystem_tags = stem_dict['analysis'][0]['gr']
                    token.pymorphy_tags = morph_analyzer.parse(stem_dict['text'])[0].tag
                    list_of_tokens.append(token)
        return list_of_tokens


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    path = Path(path_to_validate)

    if not path:
        raise UnknownDatasetError

    if not path.exists():
        raise FileNotFoundError

    if not path.is_dir():
        raise NotADirectoryError

    list_of_raws = list(path.glob('*_raw.txt'))
    list_of_metas = list(path.glob('*_meta.json'))
    if not len(list_of_raws) == len(list_of_metas):
        raise InconsistentDatasetError

    raw_ids = []
    meta_ids = []
    for raw, meta in zip(list_of_raws, list_of_metas):
        raw_ids.append(int(raw.parts[-1].split('_')[0]))
        meta_ids.append(int(meta.parts[-1].split('_')[0]))
    if sorted(raw_ids) != sorted(meta_ids):
        raise InconsistentDatasetError

    if not list(path.iterdir()):
        raise EmptyDirectoryError


def main():
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
