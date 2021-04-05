"""
Implementation of POSFrequencyPipeline for score ten only.
"""

from collections import defaultdict
import json
from pathlib import Path
import re

from constants import ASSETS_PATH
from visualizer import visualize
from pipeline import validate_dataset, CorpusManager


class POSFrequencyPipeline:
    def __init__(self, corpus_manager):
        self.corpus_manager = corpus_manager

    def run(self):
        """
        Runs pipeline visualize scenario
        """
        articles = self.corpus_manager.get_articles()
        for article in articles.values():
            processed_text_path = Path(ASSETS_PATH) / f'{article.article_id}_processed.txt'
            with open(processed_text_path, encoding='utf-8') as file:
                processed_text = file.read()

            pos_tags = defaultdict(int)
            tags = re.findall('<(.+?)>', processed_text)
            for tag in tags:
                pos = tag.split('=')[0].split(',', maxsplit=1)[0]
                pos_tags[pos] += 1

            meta_path = Path(ASSETS_PATH) / f'{article.article_id}_meta.json'
            with open(meta_path, 'a', encoding='utf-8') as json_file:
                json.dump(pos_tags, json_file, sort_keys=False, indent=4,
                          ensure_ascii=False, separators=(',', ': '))

            png_path = Path(ASSETS_PATH) / f'{article.article_id}_image.png'
            visualize(statistics=pos_tags, path_to_save=png_path)

def main():
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pos_pipeline = POSFrequencyPipeline(corpus_manager=corpus_manager)
    pos_pipeline.run()


if __name__ == "__main__":
    main()s