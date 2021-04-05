"""
Implementation of POSFrequencyPipeline for score ten only.
"""

import json
from pathlib import Path
import re

from constants import ASSETS_PATH
from pipeline import CorpusManager
from visualizer import visualize


class POSFrequencyPipeline:
    def __init__(self, corpus_manager: CorpusManager):
        self.corpus_manager = corpus_manager
        self._processed_text = ''
        self.pos_frequencies = {}

    def run(self):
        """
        Runs pipeline process scenario
        """
        articles = self.corpus_manager.get_articles()
        for file in articles.values():
            path_to_processed = Path(ASSETS_PATH) / '{}_processed.txt'.format(file.article_id)
            with open(path_to_processed, 'r', encoding='utf-8') as text_file:
                self._processed_text = text_file.read()
            self.pos_frequencies = self._calculate_frequencies()
            self._write_to_meta(file.article_id)
            visualize(statistics=self.pos_frequencies,
                      path_to_save=Path(ASSETS_PATH) / '{}_image.png'.format(file.article_id))

    def _calculate_frequencies(self):
        """
        Performs processing of each text
        """
        pos = re.findall(r"<([A-Z]+)", self._processed_text)
        pos_freq = {}
        for tag in pos:
            if tag in pos_freq:
                pos_freq[tag] += 1
            else:
                pos_freq[tag] = 1
        return pos_freq

    def _write_to_meta(self, file_id):
        path = Path(ASSETS_PATH) / '{}_meta.json'.format(file_id)
        with open(path, encoding="utf-8") as file:
            meta = json.load(file)
            meta['pos_frequencies'] = self.pos_frequencies
        with open(path, "w", encoding="utf-8") as file:
            json.dump(meta, file)


def main():
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = POSFrequencyPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
