"""
Useful constant variables
"""

import os

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
ASSETS_PATH = os.path.join(PROJECT_ROOT, 'tmp', 'articles')
CRAWLER_STATE = os.path.join(PROJECT_ROOT, 'tmp', 'crawler.state')
PARSER_STATE = os.path.join(PROJECT_ROOT, 'tmp', 'parser.state')

CRAWLER_CONFIG_PATH = os.path.join(PROJECT_ROOT, 'crawler_config.json')

HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
           'referer': 'http://www.gazetaeao.ru/'}

COOKIES = {'beget': 'begetok'}
