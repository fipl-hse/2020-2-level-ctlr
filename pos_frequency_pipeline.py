"""
Implementation of POSFrequencyPipeline for score ten only.
"""
import os
import re
import json

from constants import ASSETS_PATH
from visualizer import visualize


class POSFrequencyPipeline:
    def __init__(self, assets):
        self.assets = assets
        self._processed_text = ''
        self.frequencies_dict = {}

    def run(self):
        """
        Runs POSFrequency pipeline process scenario
        """
        for article_id, article in self.assets.get_articles().items():

            processed_path = article._get_processed_text_path()
            with open(processed_path, 'r') as file:
                self._processed_text = file.read()

            self._process()
            self._add_pos_to_metadata(article_id)
            path_png = f'{article_id}_image.png'
            visualize(statistics=self.frequencies_dict, path_to_save=os.path.join(ASSETS_PATH, path_png))

    def _process(self):
        result = re.findall(r'<[A-Z]+', self._processed_text)
        print(result)
        for pos in result:
            self.frequencies_dict[pos[1:]] = self.frequencies_dict.get(pos[1:], 0) + 1

    def _add_pos_to_metadata(self, file_id):
        path_meta = f'{file_id}_meta.json'
        with open(os.path.join(ASSETS_PATH, path_meta), 'r', encoding='utf-8') as file:
            meta = json.load(file)

        meta['pos_frequencies'] = self.frequencies_dict
        with open(os.path.join(ASSETS_PATH, path_meta), 'w', encoding='utf-8') as fp:
            json.dump(meta, fp, ensure_ascii=False, indent=2)
