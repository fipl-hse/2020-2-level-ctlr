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
        self._processed_text = ''

    def run(self):
        storage = self.assets.get_articles()

        for article_id, article in storage.items():
            processed_path = article._get_processed_text_path()

            with open(processed_path, 'r') as file:
                self._processed_text = file.read()
            self._process()
            self._add_pos_to_metadata(article_id)
            visualize(statistics=self.pos_frequencies, path_to_save=f'{ASSETS_PATH}\\{article_id}_image.png')

    def _process(self):
        result = re.findall(r'<[A-Z]*', self._processed_text)
        pos = {}

        for pos_tag in result:
            pos[pos_tag[1:]] = pos.get(pos_tag[1:], 0) + 1

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
