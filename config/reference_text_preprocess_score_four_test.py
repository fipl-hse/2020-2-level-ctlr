import re
import os
import json
import unittest
from constants import ASSETS_PATH
from pipeline import CorpusManager, TextProcessingPipeline, validate_dataset
from config.test_params import TEST_FILES_FOLDER


class ReferenceTextPreprocessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with open(os.path.join(TEST_FILES_FOLDER, "0_raw.txt")) as f:
            text = f.read()
        with open(os.path.join(ASSETS_PATH, "0_raw.txt"), "w", encoding="utf-8") as r:
            r.write(text)

        validate_dataset(ASSETS_PATH)
        corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
        pipe = TextProcessingPipeline(corpus_manager)
        pipe.run()

    def setUp(self) -> None:
        with open('config/test_files/reference_score_four_test.txt', 'r', encoding='utf-8') as rf:
            self.reference = rf.read()
        with open(os.path.join(ASSETS_PATH, "0_processed.txt"), "r", encoding='utf-8') as pr:
            self.processed = pr.read()

    def test_reference_preprocessed_are_equal(self):
        # check number of tokens sequences
        self.assertEqual(len(self.reference.split()),
                         len(self.processed.split()),
                         msg=f"""Number of tokens sequences in reference {self.reference} 
                                                and processed {self.processed} texts is different""")

        # check tokenization
        self.assertEqual(self.reference.split(),
                         self.processed.split(),
                         msg="""Pipe do not tokenizes admin text. Check how you tokenize""")
