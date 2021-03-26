import os
import unittest
from constants import CRAWLER_CONFIG_PATH
from pipeline import EmptyDirectoryError, validate_dataset, NotADirectoryError


print("Stage 2A: Validating Assets Path")
print("Starting tests with received assets folder")


class ExtendedTestCase(unittest.TestCase):
    def assertRaisesWithMessage(self, msg, exception, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
            print(msg)
            self.assertFail()
        except Exception as inst:
            self.assertEqual(type(inst), exception)


class PipelinePathCheck(ExtendedTestCase):
    def test_pipe_fails_if_path_not_exists(self):
        not_existing_path = "plain_text"

        error_message = """Checking that scrapper can handle not existing assets paths failed. 
                        """
        self.assertRaisesWithMessage(error_message,
                                     FileNotFoundError,
                                     validate_dataset,
                                     not_existing_path)

    def test_pipe_fails_if_no_files_in_folder_path(self):
        test_dir = 'test_assets'
        os.mkdir(test_dir)

        error_message = """Checking that empty directories can not be processed failed.
                        """
        self.assertRaisesWithMessage(error_message,
                                     EmptyDirectoryError,
                                     validate_dataset,
                                     test_dir)
        os.rmdir(test_dir)

    def test_assets_path_not_directory(self):
        error_message = """Checking that pipeline fails if given not a directory path.
                        """
        self.assertRaisesWithMessage(error_message,
                                     NotADirectoryError,
                                     validate_dataset,
                                     CRAWLER_CONFIG_PATH)


print("Done")

if __name__ == "__main__":
    unittest.main()
