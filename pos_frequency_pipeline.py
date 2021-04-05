"""
Implementation of POSFrequencyPipeline for score ten only.
"""
import json
import re
from collections import Counter
from pathlib import Path

from constants import ASSETS_PATH
from pipeline import CorpusManager
from visualizer import visualize


class POSFrequencyPipeline:
    """
    Extracts POS frequencies and creates distribution plots with them.
    """

    frequencies: Counter

    def __init__(self, assets: CorpusManager):
        self.assets = assets

    def run(self):
        for idx in self.assets.get_articles().keys():
            processed_text_path = Path(ASSETS_PATH) / f"{idx}_processed.txt"
            with open(processed_text_path, encoding="utf-8") as file:
                text = file.read()

            self.frequencies = Counter(re.findall(r"(?<=<)[A-Z]+", text))
            self._update_meta(idx)

            visualize(
                statistics=self.frequencies,
                path_to_save=Path(ASSETS_PATH) / f"{idx}_image.png",
            )

    def _update_meta(self, idx):
        path = Path(ASSETS_PATH) / f"{idx}_meta.json"

        with open(path, encoding="utf-8") as file:
            article = json.load(file)
            article["frequencies"] = self.frequencies

        with open(path, "w", encoding="utf-8") as file:
            json.dump(article, file, ensure_ascii=False, indent=4)


def main():
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = POSFrequencyPipeline(assets=corpus_manager)

    pipeline.run()


if __name__ == "__main__":
    main()
