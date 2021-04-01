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
        self.corpus_manager = assets
        self.text = ''
        self.pos_freq = {}

    def run(self):
        """
        Runs pipeline process scenario
        """
        articles = self.corpus_manager.get_articles()
        for proc_article in articles.values():
            self.text = proc_article.get_raw_text()
            self.pos_freq = self._process()
            self._write_freq_meta(proc_article.article_id)
            visualize(statistics=self.pos_freq,
                      path_to_save=Path(ASSETS_PATH) / f"{proc_article.article_id}_image.png")

    def _analyze_text(self):
        """"
        Analyzes a text
        """
        return Mystem().analyze(self.text)

    def _process(self):
        """"
        Counts frequencies for parts of speech in a text
        """
        pos_frequencies = {}
        for token in self._analyze_text():
            if token.get('analysis'):
                found_pos = re.findall(r"^[A-Z]+", token["analysis"][0]["gr"])
                pos_frequencies[found_pos[0]] = pos_frequencies.get(found_pos[0], 0) + 1
        return pos_frequencies

    def _write_freq_meta(self, art_id):
        path = Path(ASSETS_PATH) / f"{art_id}_meta.json"

        with open(path, encoding="utf-8") as file:
            meta = json.load(file)
            meta['pos_frequencies'] = self.pos_freq

        with open(path, "w", encoding="utf-8") as file:
            json.dump(meta, file)


def main():
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = POSFrequencyPipeline(assets=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
