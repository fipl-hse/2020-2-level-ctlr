# Dataset Collector Lab for 2nd course of Fundamental and Computational Linguistics (2020/2021)

![Dataset collection](https://github.com/fipl-hse/2020-2-level-ctlr-admin/workflows/Crawler%20is%20functioning/badge.svg)

## About the course

["Computer Tools for Linguistic Research"](https://www.hse.ru/en/edu/courses/339579587) 
in Higher School of Economics (Nizhny Novgorod branch).

### Lectors 

* [Demidovskij Alexander Vladimirovich](https://www.hse.ru/staff/demidovs) - lector
* Uraev Dmitry Yurievich - assitant

## Motivation

The idea is to automatically obtain a dataset that has a certain structure and appropriate content,
perform morphological analysis using various NLP libraries. 
[Dataset requirements](./docs/dataset.md).

## Project Timeline

1. **Scrapper**
   1. Short summary: Your code can automatically parse a media website you are going to choose
      , save texts and its metadata in a proper format
   1. Deadline: *March 15th, 2021*
   1. Format: each student works in their own PR
   1. Dataset volume: 5-7 articles
   1. Design document: [./docs/scrapper.md](./docs/scrapper.md)
   1. Additional resources:
      1. List of media websites to select from: [link]()
1. **Pipeline**
   1. Short summary: Your code can automatically process raw texts from previous step,
      make point-of-speech tagging and basic morphological analysis.
   1. Deadline: *April 5th, 2021*
   1. Format: each student works in their own PR
   1. Dataset volume: 5-7 articles
   1. Design document: [./docs/pipeline.md](./docs/pipeline.md)
1. **Own Research**
   1. Short summary: Your code can create a bigger processed dataset of a requested volume and
      format that you use for your linguistic research.
   1. Deadline: *TBD (approx. May 30th, 2021)*
   1. Format: students work in groups - one PR per group
   1. Dataset volume: 100 articles

## Technical solution

| Module | Description | Component | I need to know them, if I want to get at least |
|:---|:---|:---|:---|
| [requests]() | module for downloading web pages | scrapper | 4 |
| [BeautifulSoup]() | module for finding information on web pages | scrapper | 4 |
| [lxml]() | module for parsing HTML as a structure | scrapper | 6 |
| [pymystem3]() | module for morphological analysis | pipeline | 6 |
| [pymorphy2]() | module for morphological analysis | pipeline | 8 |
| [pandas]() | module for table data analysis | pipeline | 10 |

Software solution is built on top of three components:
1. [scrapper.py](./scrapper.py) - a module for finding articles from the given media, extracting text and
   dumping it to the filesystem. Students need to implement it.
1. [pipeline.py](./pipeline.py) - a module for processing text: point-of-speech tagging and 
   basic morphological analysis. Students need to implement it.
1. [article.py](./article.py) - a module for article abstraction to incapsulate low-level
   manipulations with the article
 
## Resources

1. Academic performance: [link](https://docs.google.com/spreadsheets/d/1qM5Drt8Us6QewWRo7n6k_TqlgoA-F9jrtvHNzrZzHM4/edit?usp=sharing) 
1. Media websites list: [link](https://drive.google.com/file/d/13daSXTD6S-LIr0oNLBz6XeA74ZwYYsQp/view?usp=sharing)
1. Python programming course from previous semester: [link](https://github.com/fipl-hse/2020-2-level-labs)
1. Scrapping tutorials: [YouTube series (russian)](https://youtu.be/7hn1_t2ZtJQ)
