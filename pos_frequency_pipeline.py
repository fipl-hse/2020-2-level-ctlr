"""
Implementation of POSFrequencyPipeline for score ten only.
"""
import json
import re

from constants import ASSETS_PATH
from collections import Counter
from pathlib import Path
from pipeline import CorpusManager
from visualizer import visualize


class POSFrequencyPipeline:
    def __init__(self, assets):
        self.assets = assets
        self.processed_text = ''
        self.freq_list = []

    def run(self):
        numbers = self.assets.get_articles().keys()
        for number in numbers:
            processed_text_path = Path(ASSETS_PATH) / f"{number}_processed.txt"
            with open(processed_text_path, encoding="utf-8") as file:
                self.processed_text = file.read()
            self.freq_list = Counter(re.findall(r"(?<=<)[A-Z]+", self.processed_text))
            self._write_to_meta(number)
            visualize(statistics=self.freq_list, path_to_save=ASSETS_PATH + f'/{number}_image.png')

    def _write_to_meta(self, number):
        path = ASSETS_PATH + f'/{number}_meta.json'

        with open(path, encoding='utf-8') as file:
            data = json.load(file)
            data['frequencies'] = self.freq_list

        with open(path, 'w', encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)


def main():
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = POSFrequencyPipeline(assets=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
