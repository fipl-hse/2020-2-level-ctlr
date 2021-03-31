"""
Implementation of POSFrequencyPipeline for score ten only.
"""

from collections import defaultdict
import json
import os
import re

from pymystem3 import Mystem

from constants import ASSETS_PATH
from visualizer import visualize


class POSFrequencyPipeline:
    def __init__(self, corpus_manager):
        self.corpus_manager = corpus_manager
        self._current_article = None

    def run(self):
        """
        Runs pipeline process scenario
        """
        articles = self.corpus_manager.get_articles()
        for article in articles.values():
            article.text = article.get_raw_text()
            self._current_article = article
            self._process()
            self._save_meta()

            png_path = os.path.join(ASSETS_PATH, f'{self._current_article.article_id}_image.png')
            visualize(statistics=self._current_article.pos_tags,
                      path_to_save=png_path)

    def _process(self):
        self._current_article.pos_tags = defaultdict(int)
        text = self._current_article.text
        text = ' '.join(re.findall(r'\w+', text.lower()))
        result = Mystem().analyze(text)

        for word in result[::2]:  # skip whitespaces
            try:
                pos = word['analysis'][0]['gr'].split('=')[0].split(',', maxsplit=1)[0]
            except (KeyError, IndexError):
                continue
            self._current_article.pos_tags[pos] += 1

    def _save_meta(self):
        meta_path = os.path.join(ASSETS_PATH, f'{self._current_article.article_id}_meta.json')
        with open(meta_path, encoding='utf-8') as json_file:
            meta = json.load(json_file)

        meta['pos_tags'] = self._current_article.pos_tags

        with open(meta_path, 'w', encoding='utf-8') as file:
            json.dump(meta, file, sort_keys=False, indent=4,
                      ensure_ascii=False, separators=(',', ': '))
