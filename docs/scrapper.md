~~~~# Retrieve raw data from World Wide Web

> Python competencies required to complete this tutorial:
> * working with external dependencies, going beyond Python standard library
> * working with external modules: local and downloaded from PyPi
> * working with files: create/read/update
> * downloading web pages
> * parsing web pages as HTML structure

Scraping as a process contains following steps:
1. crawling the web-site and collecting all pages that satisfy given criteria
1. downloading selected pages content
1. extracting specific content from downloaded pages
1. saving necessary information

As a part of the first milestone, you need to implement scrapping logic as a `scrapper.py` module.
When it is run as a standalone Python program, it should all aforementioned stages.

## Executing scrapper

Example execution (`Windows`):

```bash
py scrapper.py
```

Expected result:
1. `N` articles from the given URL are parsed
1. all articles are downloaded to the `tmp/articles` directory. `tmp` directory content:
```
+-- 2020-2-level-ctlr
    +-- tmp
        +-- articles
            +-- 1_raw.txt <- the paper with the ID as the name
            +-- 1_meta.json <- the paper meta-information
            +-- ...
```

> NOTE: When using CI (Continuous Integration), generated `dataset.zip` is available in
> build artifacts. Go to `Actions` tab in GitHub UI of your fork, open the last job and
> if there is an artifact, you can download it.

## Configuring scrapper

Scrapper behaviour is fully defined by a configuration file that is called 
`crawler_config.json` and it is placed at the same level as `scrapper.py`. It is JSON file,
simply speaking it is a set of key-value pairs. 


|Config parameter|Description|Possible values|
|:---|:---|:---|
|`"base_urls"`| entrypoints for crawling. Can contain several URLs as there is no guarantee that there will be enough articles on a single page|A list of URLs, for example `["https://www.nn.ru/text/?page=2", "https://www.nn.ru/text/?page=3"]`|
|`total_articles_to_find_and_parse`|Number of articles to parse|Integer values, should work for at least `100` papers|
|`max_number_articles_to_get_from_one_seed`|Number of articles to find from one seed|Integer values, usually equals to the value of `total_articles_to_find_and_parse`|

## Assessment criteria

You state your abmitions on the mark by editing the file `target_score.txt` at the `line 2`. For example, such content:
```
# Target score for scrapper.py:
6
...
```
would mean that you have made tasks for mark `6` and request mentors to check if you can get it.

1. Desired mark: **4**:
   1. pylint level: `5/10`
   1. scrapper validates config and fails appropriately if the latter is incorrect
   1. scrapper downloads articles from the selected newspaper
   1. scrapper produces only `_raw.txt` files in the `tmp/articles` directory (*no metadata*)
1. Desired mark: **6**:
   1. pylint level: `7/10`
   1. all requirements for the mark **4**
   1. scrapper produces `_meta.json` files for each article, however, it is allowed for each
      meta file to contain reduced number of keys: `id`, `title`, `author`, `url` 
1. Desired mark: **8**:
   1. pylint level: `10/10`
   1. all requirements for the mark **6**
   1. scrapper produces `_meta.json` files for each article, meta file should be full: 
      `id`, `title`, `author`, `url`, `date`.
1. Desired mark: **10**:
   1. pylint level: `10/10`
   1. all requirements for the mark **8**
   1. scrapper can visit all website pages while config contains only one seed.

> NOTE: date should be in the special format. Read [dataset description](./dataset.md) 
> for technical details
