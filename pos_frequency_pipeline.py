"""
Implementation of POSFrequencyPipeline for score ten only.
"""
from article import Article
from constants import ASSETS_PATH
from collections import Counter
from pipeline import CorpusManager
from pymystem3 import Mystem


class POSFrequencyPipeline:
    def __init__(self, assets):
        self.assets = assets
        self.raw_text = ''

    def run(self):
        numbers = self.assets.get_articles()
        for number in numbers:
            article = Article(url=None, article_id=number)
            self.raw_text = article.get_raw_text()
            freq_list = self._process()
            print(freq_list)

    def _process(self):
        """
        Performs processing of each text
        """
        result = Mystem().analyze(self.raw_text)
        list_of_tokens = []
        for stem_dict in result:
            if stem_dict.get('analysis'):
                normalized_form = stem_dict['analysis'][0]['lex']
                list_of_tokens.append(normalized_form)
        freq_list = Counter(list_of_tokens)
        return freq_list


def main():
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = POSFrequencyPipeline(assets=corpus_manager)
    pipeline.run()

if __name__ == "__main__":
    main()