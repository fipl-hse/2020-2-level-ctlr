"""
Implementation of POSFrequencyPipeline for score ten only.
"""
import os
import re

# from pipeline import CorpusManager
from visualizer import visualize

from constants import ASSETS_PATH


class POSFrequencyPipeline:
    def __init__(self, corpus_manager):
        self.corpus = corpus_manager

    def run(self):
        frequencies = self._count_frequencies()
        visualize(frequencies, os.path.join(ASSETS_PATH, 'pos_frequencies.png'))

    def _count_frequencies(self):
        articles = self.corpus.get_articles()
        tags_found = []
        for index, article in articles.items():
            article_path = os.path.join(ASSETS_PATH, f'{index}_processed.txt')
            with open(article_path, encoding='utf-8') as file:
                contents = file.read()
                tags_found.extend(re.findall(r"<([A-Z]*)[,=]?", contents))
        frequencies = {}
        for tag in tags_found:
            frequencies[tag] = tags_found.count(tag)
        return frequencies


if __name__ == "__main__":
    pass
