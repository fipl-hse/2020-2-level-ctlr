import re
import os
import unittest
from constants import ASSETS_PATH


TAGS = ["A", "ADV", "S", "V", "PR", "ANUM", "CONJ", "SPRO", "APRO", "PART", "NUM", "ADVPRO"]


class StudentTextPreprocessTest(unittest.TestCase):
    def setUp(self) -> None:
        self.articles = dict()
        for article in os.listdir(ASSETS_PATH):
            if article.endswith("_processed.txt"):
                with open(os.path.join(ASSETS_PATH, article), "r", encoding="utf-8") as txt:
                    self.articles[int(article[0])] = txt.read()

    @staticmethod
    def custom_split(string) -> list:
        return [element+'>' for element in string.split('>')][:-1]

    def test_tagging_format_tokens_format(self):
        for article_id, article_text in self.articles.items():
            word_tag_sequences = self.custom_split(article_text)
            for sequence in word_tag_sequences:
                self.assertEqual(sequence[-1], ">",
                                 msg=f"{sequence} --- There should be > at the end of each word<tag> sequence")
                self.assertTrue("<" in sequence,
                                msg=f"{sequence} --- < markup symbol should be in processed text")
                self.assertTrue(sequence[sequence.index("<") - 1].isalpha(),
                                msg=f"{sequence} --- In tagged sequence there should be char symbol before < ")

    def test_tags_correctness(self):
        for article_id, article_text in self.articles.items():
            tags = re.findall(r"<([A-Z]+)[,=]?", article_text)
            for tag in tags:
                self.assertTrue(tag in TAGS,
                                msg=f"""Tag {tag} not in list of known mystem tags""")
