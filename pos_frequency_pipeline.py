"""
Implementation of POSFrequencyPipeline for score ten only.
"""
import json
import re

from article import Article
from constants import ASSETS_PATH
from collections import Counter
from pipeline import CorpusManager
from pymystem3 import Mystem
from visualizer import visualize


class POSFrequencyPipeline:
    def __init__(self, assets):
        self.assets = assets
        self.raw_text = ''
        self.freq_list = []

    def run(self):
        numbers = self.assets.get_articles()
        for number in numbers:
            article = Article(url=None, article_id=number)
            self.raw_text = article.get_raw_text()
            self.freq_list = self._process()
            self._write_to_meta(number)
            visualize(statistics=self.freq_list, path_to_save=ASSETS_PATH + f'/{number}_image.png')

    def _process(self):
        """
        Performs processing of each text
        """
        result = Mystem().analyze(self.raw_text)
        list_of_pos = []
        for stem_dict in result:
            if stem_dict.get('analysis'):
                pos = re.match(r'[A-Z]+', stem_dict['analysis'][0]['gr']).group()
                list_of_pos.append(pos)
        freq_list = Counter(list_of_pos)
        return freq_list

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
