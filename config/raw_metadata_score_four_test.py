import os
import unittest
from constants import ASSETS_PATH


class RawDataValidator(unittest.TestCase):
    def setUp(self) -> None:
        # open and prepare texts
        self.texts = []
        for file_name in os.listdir(ASSETS_PATH):
            if file_name.endswith("_raw.txt"):
                with open(os.path.join(ASSETS_PATH, file_name), encoding='utf-8') as f:
                    file = f.read()
                    self.texts.append((int(file_name[0]), file))
        self.texts = tuple(self.texts)

    def test_validate_sort(self):
        list_ids = [pair[0] for pair in self.texts]
        for i in range(1, len(list_ids)+1):
            self.assertTrue(i in list_ids,
                            msg="""Articles ids are not homogeneous. E.g. numbers are not from 1 to N""")

    def test_texts_are_not_empty(self):
        for file_name in self.texts:
            self.assertTrue(len(file_name[1]) > 50,
                            msg="""Text with ID: {} seems to be empty (less than 50 characters).
                            Check if you collected article correctly""".format(file_name[0]))


if __name__ == "__main__":
    unittest.main()
