# Article module

The Article module exposes a class `Article` that models web article that is
downloaded and parsed. It is responsible for several aspects:

1. Storing article information: url, id, title, etc.
1. File I/O (stands for Input/Output): reading and writing of article raw text,
   processed text and its meta-information

This module is functional and given to you for further usage. Feel free to 
inspects its content. In case you think you have found a mistake, contact
assistant. Those who considerably improve this module will get additional 
bonuses.

> **HINT:** for Crawler implementation you need following methods:
> * `Article.__init__(...)`
> * `Article.save_raw(...)`

> **HINT:** for Pipeline implementation you need following methods:
> * `Article.from_meta_json(...)`
> * `Article.get_raw_text(...)`
> * `Article.save_processed(...)`
