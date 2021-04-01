"""
Implementation of POSFrequencyPipeline for score ten only.
"""
import re
from pathlib import Path

from pymystem3 import Mystem

from visualizer import visualize


class POSFrequencyPipeline:
    def __init__(self, corpus_manager):
        self.corpus_manager = corpus_manager

    def run(self):
        """
        Runs POSFrequency pipeline process scenario
        """
        for article_id, article in self.corpus_manager.get_articles().items():
            #for file in Path(self.path_to_raw_txt_data).glob('*_processed.txt'):
            text = article.get_raw_text()
            frequencies_dict = {}
            result = Mystem().analyze(text)
            for word in result:
                try:
                    pos = re.search(r'[A-Z]+', word['analysis'][0]['gr']).group()
                    frequencies_dict[pos] = frequencies_dict.get(pos, 0) + 1
                except (KeyError, IndexError):
                    continue
            visualize(statistics=frequencies_dict, path_to_save=f'.\\tmp\\articles\\{article_id}_image.png')
