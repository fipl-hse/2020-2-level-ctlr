"""
Implementation of POSFrequencyPipeline for score ten only.
"""

import json
import re

from pymystem3 import Mystem

from constants import ASSETS_PATH
from pipeline import CorpusManager
from visualizer import visualize


class POSFrequencyPipeline:
    def __init__(self, assets):
        self.assets = assets
        self.pos_frequencies = {}
        self._text = ''

    def run(self):
        storage = self.assets.get_articles()

        for article_id, article in storage.items():
            self._text = article.get_raw_text()
            self._process()
            self._add_pos_to_metadata(article_id)
            visualize(statistics=self.pos_frequencies, path_to_save=f'{ASSETS_PATH}\\{article_id}_image.png')

    def _process(self):
        result = Mystem().analyze(self._text)
        pos = {}

        for word in result:
            if 'analysis' in word and word['analysis']:
                tags = word['analysis'][0]['gr']
                pos_tag = re.match(r'[A-z]+', tags).group()
                pos[pos_tag] = pos.get(pos_tag, 0) + 1

        self.pos_frequencies = pos

    def _add_pos_to_metadata(self, file_id):
        path = f'{ASSETS_PATH}\\{file_id}_meta.json'

        with open(path, 'r', encoding='utf-8') as file:
            meta = json.load(file)

        meta['pos_frequencies'] = self.pos_frequencies

        with open(path, 'w', encoding='utf-8') as file:
            json.dump(meta, file)


def main():
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = POSFrequencyPipeline(corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
