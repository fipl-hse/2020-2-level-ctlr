"""
Implementation of POSFrequencyPipeline for score ten only.
"""
import re

from pathlib import Path

from visualizer import visualize
from pipeline import CorpusManager

from constants import ASSETS_PATH


class POSFrequencyPipeline:
    def __init__(self, corpus: CorpusManager):
        self.corpus = corpus
        self.current_article = None

    def run(self):
        articles = self.corpus.get_articles()
        for article in articles.values():
            self.current_article = article
            frequencies = self._count_frequencies()
            self._update_meta(frequencies)
            path = Path(ASSETS_PATH) / f'{article.article_id}_image.png'
            visualize(frequencies, path)

    def _count_frequencies(self):
        path = Path(ASSETS_PATH) / f'{self.current_article.article_id}_processed.txt'
        with open(path, encoding='utf-8') as file:
            contents = file.read()
        tags_found = re.findall(r"<([A-Z]+)[,=]?", contents)
        frequencies = {}
        for tag in tags_found:
            frequencies[tag] = tags_found.count(tag)
        return frequencies

    def _update_meta(self, frequencies):
        meta_path = Path(ASSETS_PATH) / f'{self.current_article.article_id}_meta.json'
        article = self.current_article.from_meta_json(meta_path)
        article.pos_frequencies = frequencies
        article.text = article.get_raw_text()
        article.save_raw()


def main():
    corpus_manager = CorpusManager(ASSETS_PATH)
    visualizer = POSFrequencyPipeline(corpus_manager)
    visualizer.run()


if __name__ == "__main__":
    main()
