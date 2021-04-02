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
            path = Path(ASSETS_PATH) / f"{proc_article.article_id}_processed.txt"
            with open(path, encoding='utf-8') as file:
                self.text = file.read()
            self.pos_freq = self._count_freq()
            self._write_freq_meta(proc_article.article_id)
            visualize(statistics=self.pos_freq,
                      path_to_save=Path(ASSETS_PATH) / f"{proc_article.article_id}_image.png")

    def _count_freq(self):
        """"
        Counts frequencies for parts of speech in a text
        """
        pos_frequencies = {}
        found_pos = re.findall(r"^[A-Z]+", self.text)
        for pos in found_pos:
            pos_frequencies[pos] = pos_frequencies.get(pos, 0) + 1
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
