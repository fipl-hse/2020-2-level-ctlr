"""
Implementation of POSFrequencyPipeline for score ten only.
"""
import re
import pathlib
import json

from constants import ASSETS_PATH
from visualizer import visualize


class POSFrequencyPipeline:
    def __init__(self, assets):
        self.corpus_manager = assets
        self._text = ''

    def run(self):
        for article in self.corpus_manager.get_articles().values():
            self._text = self._get_processed_text(article.article_id)
            freq_dict = self._calculate_pos_frequency()
            self._write_to_meta_file(article.article_id, freq_dict)
            graph_image_path = pathlib.Path(ASSETS_PATH) / f'{article.article_id}_image.png'
            visualize(statistics=freq_dict, path_to_save=graph_image_path)

    @staticmethod
    def _get_processed_text(article_id):
        processed_text_path = pathlib.Path(ASSETS_PATH) / f'{article_id}_processed.txt'
        with open(processed_text_path, encoding='utf-8') as processed_file:
            return processed_file.read()

    def _calculate_pos_frequency(self):
        freq_dict = {}
        pos_list = re.findall(r'(?<=<)[A-Z]+', self._text)
        for pos in pos_list:
            if pos not in freq_dict:
                freq_dict[pos] = 1
            else:
                freq_dict[pos] += 1

        return freq_dict

    @staticmethod
    def _write_to_meta_file(article_id, freq_dict):
            meta_file_path = pathlib.Path(ASSETS_PATH) / f'{article_id}_meta.json'
            with open(meta_file_path, 'r+', encoding='utf-8') as meta_file:
                data = json.load(meta_file)
                data['pos frequency'] = freq_dict
                meta_file.seek(0)
                json.dump(data,
                          meta_file,
                          sort_keys=False,
                          indent=4,
                          ensure_ascii=False,
                          separators=(',', ': '))
