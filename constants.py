"""
Useful constant variables
"""

import os

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
ASSETS_PATH = os.path.join(PROJECT_ROOT, 'tmp', 'articles')
CRAWLER_CONFIG_PATH = os.path.join(PROJECT_ROOT, 'crawler_config.json')

HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'}