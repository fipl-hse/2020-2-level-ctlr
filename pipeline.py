"""
Pipeline 
"""

from pathlib import Path
from typing import List
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
    def __init__(self, original_word, normalized_form):
        self.original_word = original_word
        self.normalized_form = normalized_form
        self.mystem_tags = ''

    def __str__(self):
        return f"{self.normalized_form}<{self.mystem_tags}>"

    def public_method(self):
        pass


class CorpusManager:
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
            ind = str(one_file).split('\\')[-1].split('_')[0]
            self._storage[ind] = Article(url=None, article_id=ind)

    def get_articles(self):
        return self._storage

    def public_method_2(self):
        pass


class TextProcessingPipeline:
    def __init__(self, corpus_manager: CorpusManager):
        self.corpus_manager = corpus_manager
        self.text = ''

    def run(self):
        articles = self.corpus_manager.get_articles()
        for article in articles.values():
            self.text = article.get_raw_text()
            morph_tokens = self._process()
            processed_text = []
            for morph_token in morph_tokens:
                processed_text.append(str(morph_token))
            article.save_processed(' '.join(processed_text))

    def _process(self) -> List[type(MorphologicalToken)]:
        result = Mystem().analyze(self.text)
        tokens = []

        for token in result:
            if token.get('analysis') and token.get('text'):
                if token['analysis'][0].get('lex') and token['analysis'][0].get('gr'):
                    morph_token = MorphologicalToken(token['text'], token['analysis'][0]['lex'])
                    morph_token.mystem_tags = token['analysis'][0]['gr']
                    tokens.append(morph_token)
        return tokens

    def public_method_3(self):
        pass


def validate_dataset(path_to_validate):
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
