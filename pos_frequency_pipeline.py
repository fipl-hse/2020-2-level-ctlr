"""
Implementation of POSFrequencyPipeline for score ten only.
"""
import json
import re
from collections import Counter
from pathlib import Path

from pymystem3 import Mystem

from article import Article
from constants import ASSETS_PATH
from pipeline import CorpusManager
from visualizer import visualize


class POSFrequencyPipeline:
    def __init__(self, assets: CorpusManager):
        self.assets = assets
        self.text = ""
        self.frequencies = Counter()

    def run(self):
        for idx in self.assets.get_articles():
            article = Article(url=None, article_id=idx)
            self.text = article.get_raw_text()
            self.frequencies += self._process()
            self._update_meta(idx)
            visualize(
                statistics=self.frequencies,
                path_to_save=Path(ASSETS_PATH) / f"{idx}_image.png",
            )

    def sample(self):
        raise NotImplementedError

    def _process(self):
        result = Mystem().analyze(self.text)

        frequencies = Counter()

        for token in result:

            if token.get("analysis"):
                pos = re.match(r"^[A-Z]+", token["analysis"][0]["gr"]).group()
                frequencies.update([pos])

        return frequencies

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
