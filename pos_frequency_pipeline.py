"""
Implementation of POSFrequencyPipeline for score ten only.
"""

import json
from pathlib import Path
import re

from pymystem3 import Mystem

from constants import ASSETS_PATH
from pipeline import CorpusManager
from visualizer import visualize


class POSFrequencyPipeline:
    def __init__(self, assets):
        self.assets = assets
        self.text_to_process = ''
        self.pos_frequencies = {}

    def run(self):
        """
        Runs pipeline process scenario
        """
        articles = self.assets.get_articles()
        for file in articles.values():
            self.text_to_process = file.get_raw_text()
            self.pos_frequencies.update(self._process())
            self._write_to_meta(file.article_id)
            visualize(statistics=self.pos_frequencies,
                      path_to_save=Path(ASSETS_PATH) / '{}_image.png'.format(file.article_id))

    def _process(self):
        """
        Performs processing of each text
        """
        mystem_analyser = Mystem()
        result = mystem_analyser.analyze(self.text_to_process)
        pos_freq = {}
        for word in result:
            if word.get('analysis'):
                pos = re.findall(r"^[A-Z]+", word["analysis"][0]["gr"])
                if pos[0] in pos_freq:
                    pos_freq[pos[0]] += 1
                else:
                    pos_freq[pos[0]] = 1
        return pos_freq

    def _write_to_meta(self, file_id):
        path = Path(ASSETS_PATH) / '{}_meta.json'.format(file_id)
        with open(path, encoding="utf-8") as file:
            meta = json.load(file)
            meta['pos_frequencies'] = self.pos_frequencies
        with open(path, "w", encoding="utf-8") as file:
            json.dump(meta, file)

    def public_method(self):
        pass


def main():
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = POSFrequencyPipeline(assets=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
