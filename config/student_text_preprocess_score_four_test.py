import os
import unittest
from constants import ASSETS_PATH

PUNCTUATION_MARKS = [',', '.', '-', ';', ':', '!', '?', '<']


class StudentTextPreprocessTest(unittest.TestCase):
    def setUp(self) -> None:
        self.articles = dict()
        for article in os.listdir(ASSETS_PATH):
            if article.endswith("_processed.txt"):
                with open(os.path.join(ASSETS_PATH, article), "r", encoding="utf-8") as txt:
                    self.articles[int(article[:-8])] = txt.read()

    def test_tagging_format_tokens_format(self):
        for article_id, article_text in self.articles.items():
            for token in article_text.split():
                self.assertTrue(token not in PUNCTUATION_MARKS,
                                msg=f"""There are some punctuation marks found in article {article_id}""")
                self.assertTrue(token.islower(),
                                msg=f"""Token {token} in article {article_id} is not lowercased""")
