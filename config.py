"""
Config implementation
"""

import json
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Config:
    path: str

    def __post_init__(self):
        with open(self.path, encoding="utf-8") as file:
            attrs = json.load(file)

        self.base_urls: List[str] = attrs.get("base_urls")
        self.total_articles_to_find_and_parse: int = attrs.get(
            "total_articles_to_find_and_parse"
        )
        self.max_number_articles_to_get_from_one_seed: int = attrs.get(
            "max_number_articles_to_get_from_one_seed"
        )
        self.headers: Dict[str, str] = attrs.get("headers")
        self.cookies: Dict[str, str] = attrs.get("cookies")

    def __getitem__(self, item):
        return getattr(self, item)
