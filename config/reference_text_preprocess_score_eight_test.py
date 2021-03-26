import re
import os
import json
import unittest
from constants import ASSETS_PATH
from pipeline import CorpusManager, TextProcessingPipeline, validate_dataset
from config.test_params import TEST_FILES_FOLDER


TAGS = ["A", "ADV", "S", "V", "PR", "ANUM"]


class ReferenceTextPreprocessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with open(os.path.join(TEST_FILES_FOLDER, '0_meta.json')) as f:
            admin_meta = json.load(f)
        with open(os.path.join(ASSETS_PATH, "0_meta.json"), "w", encoding='utf-8') as f:
            json.dump(admin_meta, f)

        text = 'Красивая - мама красиво, мыла раму во второй реке.'
        with open(os.path.join(ASSETS_PATH, "0_raw.txt"), "w", encoding="utf-8") as r:
            r.write(text)

        validate_dataset(ASSETS_PATH)
        corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
        pipe = TextProcessingPipeline(corpus_manager)
        pipe.run()

    def setUp(self) -> None:
        with open('config/test_files/reference_score_eight_test.txt', 'r', encoding='utf-8') as rf:
            self.reference = rf.read()
        with open(os.path.join(ASSETS_PATH, "0_processed.txt"), "r", encoding='utf-8') as pr:
            self.processed = pr.read()
        self.re_pattern = r"\w+<*>\(*\)"

    def test_reference_preprocessed_are_equal(self):
        # check number of token word<tag> sequences
        self.assertEqual(len(self.reference.split()),
                         len(self.processed.split()),
                         msg=f"""Number of word<tag>(tag) sequences in reference {self.reference} 
                                                and processed {self.processed} texts is different""")

    def test_overall_format(self):
        # check correctness of word<tag> sequences
        for word_tag in self.processed.split():
            try:
                self.assertEqual(word_tag[-1], ")",
                                 msg=f"{word_tag} --- There should be ) at the end of each word<tag>(tag) sequence")
            except AssertionError:
                self.assertTrue(word_tag[-1].isalpha())
            try:
                self.assertTrue("<" in word_tag,
                                msg=f"{word_tag} --- < markup symbol should be in processed text")
            except AssertionError:
                self.assertTrue(word_tag[0].isalpha() and (word_tag[-1] == ")"))
            try:
                self.assertTrue(word_tag[word_tag.index("<")-1].isalpha(),
                                msg=f"{word_tag} --- In tagged sequence there should be char symbol before < ")
            except ValueError:
                self.assertTrue(word_tag[0].isalpha() and (word_tag[-1] == ")"))
            try:
                self.assertEqual(word_tag[word_tag.index(">")+1], "(",
                                 msg=f"{word_tag} --- There should be ( after > in the word<tag>(tag) sequence")
            except ValueError:
                self.assertTrue(word_tag[0].isalpha() and (word_tag[-1] == ")"))

    def test_tag_format(self):
        # check TAGS ander each sequences:
        tags_pattern = r"<([A-Z]+)[,=]{1}"
        reference_tags = re.findall(tags_pattern, self.reference)
        processed_tags = re.findall(tags_pattern, self.processed)

        # check tag correctness.
        # Optional, but should be the same across each tagger, as reference example is too simple
        for tag in processed_tags:
            self.assertTrue(tag in TAGS,
                            msg=f"Tag {tag} is not known. Is it in required tags list?")
        self.assertEqual(reference_tags, processed_tags,
                         msg=f"""Tag sequence from reference text {reference_tags}
                                    differs from processed text {processed_tags}""")

    def test_pymorphy_tag_format(self):
        reference_tags = self.reference.split()
        processed_tags = self.processed.split()
        self.assertEqual(reference_tags, processed_tags,
                         msg=f"""Tag sequence from reference text {reference_tags}
                                            differs from processed text {processed_tags}""")
