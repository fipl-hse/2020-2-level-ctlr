"""
Generates config with flexible params for testing purposes
"""

import os
import shutil
import json
from config.test_params import TEST_PATH, TEST_CRAWLER_CONFIG_PATH


def generate_config(base_urls: list, num_articles: int, path: str = TEST_CRAWLER_CONFIG_PATH):
    config = dict()
    config['base_urls'] = base_urls
    config['total_articles_to_find_and_parse'] = num_articles

    if os.path.exists(TEST_CRAWLER_CONFIG_PATH):
        shutil.rmtree(TEST_PATH)
    os.mkdir(TEST_PATH)
    with open(path, "w", encoding='utf-8') as f:
        json.dump(config, f)
