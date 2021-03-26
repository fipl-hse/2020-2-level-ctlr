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

        with open(os.path.join(TEST_FILES_FOLDER, "0_raw.txt")) as f:
            text = f.read()
        with open(os.path.join(ASSETS_PATH, "0_raw.txt"), "w", encoding="utf-8") as r:
            r.write(text)

        validate_dataset(ASSETS_PATH)
        corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
        pipe = TextProcessingPipeline(corpus_manager)
        pipe.run()

    def setUp(self) -> None:
        with open('config/test_files/reference_test.txt', 'r', encoding='utf-8') as rf:
            self.reference = rf.read()
        with open(os.path.join(ASSETS_PATH, "0_processed.txt"), "r", encoding='utf-8') as pr:
            self.processed = pr.read()
        self.re_pattern = r"\w+<*>"

    def test_reference_preprocessed_are_equal(self):
        # check number of token word<tag> sequences
        self.assertEqual(len(re.findall(self.re_pattern, self.reference)),
                         len(re.findall(self.re_pattern, self.processed)),
                         msg=f"""Number of word<tag> sequences in reference {self.reference} 
                                                and processed {self.processed} texts is different""")

    def test_overall_format(self):
        # check correctness of word<tag> sequences
        for word_tag in self.processed.split():
            self.assertEqual(word_tag[-1], ">",
                             msg=f"{word_tag} --- There should be > at the end of each word<tag> sequence")
            self.assertTrue("<" in word_tag,
                            msg=f"{word_tag} --- < markup symbol should be in processed text")
            self.assertTrue(word_tag[word_tag.index("<")-1].isalpha(),
                            msg=f"{word_tag} --- In tagged sequence there should be char symbol before < ")

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
