"""
Useful constant variables
"""

import os

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
ASSETS_PATH = os.path.join(PROJECT_ROOT, 'tmp', 'articles')
CRAWLER_CONFIG_PATH = os.path.join(PROJECT_ROOT, 'crawler_config.json')
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/88.0.4324.152 YaBrowser/21.2.3.100 Yowser/2.5 Safari/537.36'
    }
