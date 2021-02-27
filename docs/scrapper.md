# Retrieve raw data from World Wide Web

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

## Implementation tactics

> NOTE: all logic that instantiates needed abstractions and uses them should be implemented
> on the module level of the `scrapper.py`, in a special block
```py
if __name__ == '__main__':
   print('Your code goes here')
```

### Stage 0. Choose the media

Start your implementation from selection of the website you are going to scrap.
Select the website that interests you mostly and if you want to work on a mark
higher that 4 make sure it exposes all necessary information. Read more in the 
[course overview](../README.md) in the milestones section.

### Stage 1. Validate config first

Scrapper is configured by a special `crawler_config.json`.
Very first thing that should happen after scrapper is run is validation of the config.

Interface to implement:

```py
def validate_config(crawler_path):
    pass
```

`crawler_path` is the path to the config of the crawler. It is mandatory to call this
method with passing a global variable `CRAWLER_CONFIG_PATH` that should be properly
imported from the `constants.py` module.

Example call:

```py
seed_urls, max_articles, max_articles_per_seed = validate_config(CRAWLER_CONFIG_PATH)
```

* `seed_urls` - is a list of URLs specified in the config with a parameter 
`base_urls`
* `max_articles` - is a number of articles to retrieve
specified in the config with a parameter 
`total_articles_to_find_and_parse`
* `max_articles_per_seed` - is a number of articles to retrieve
specified in the config with a parameter 
`max_number_articles_to_get_from_one_seed`

When config is not correct:

1. one of the following errors is thrown (names of 
   errors are self-explaining):
   `IncorrectURLError`, `NumberOfArticlesOutOfRangeError`, 
   `IncorrectNumberOfArticlesError`, and throw `UnknownConfigError` if
   any other inconsstency is found.
2. script immediately finishes execution

### Stage 2. Find necessary number of article URLs

### Stage 2.1 Introduce Crawler abstraction

Crawler is an entity that visits `seed_urls` with the intention to collect
URLs with articles that should be parsed later.

Crawler should be instantiated with the following instruction:

```py
crawler = Crawler(seed_urls=seed_urls, 
                  total_max_articles=max_articles, 
                  max_articles_per_seed = max_articles_per_seed)
```

Crawler instance saves all constructor arguments in attributes with
corresponding names. Each instance should also have an
additional attribute `self.urls`, initialized with empty list.

### Stage 2.2 Implement method for collection of article URLs

Once the crawler is instantiated, it can be started by executing its 
method:

```py
crawler.find_articles()
```

The method should contain logic for iteraring over the list of seeds, 
downloading them and extracting article URLs from it. As a result, 
the internal attribute `self.urls`
should be filled with collected URLs.

> NOTE: crawling should find required number of articles

> NOTE: here the conditions how to find articles on the seed page
> will vary depending on the selected newspaper.


### Stage 3. Extract data from every article page

### Stage 3.1 Introduce ArticleParser abstraction

ArticleParser is an entity that is responsible for extraction of all needed information
from a single article webpage. This brings requirements on how this parser should be
initialized:

```py
parser = ArticleParser(article_url=full_url, article_id=i)
```

ArticleParser instance saves all constructor arguments in attributes with
corresponding names. Each instance should also have an
additional attribute `self.article`, initialized with a new instance of Article class.

Article is an abstraction that is implemented for you and you have to use it in your
implementation. More detailed description of the Article class can be found
[here](./article.md).

### Stage 3.2 Implement main ArticleParser method

ArticleParser interface includes a single method `parse` that incapsulates the logic
of extracting all necessary data from the article webpage. It should do following things:

1. dowload the webpage
1. initialize BeautifulSoup object on top of downloaded page (we will call it `article_bs`)
1. fill Article instance by calling private methods to extract text 
   (more details in next sections).

`parse` method usage is straightforward:
```py
article = parser.parse()
```

As you can see, `parse` method returns the instance of Article that is stored in 
`self.article` field.

### Stage 3.3 Implement extraction of text from article page

Extraction of the text should happen in the private ArticleParser method
`_fill_article_with_text`:

```py
def _fill_article_with_text(self, article_bs):
   pass
```

> NOTE: method receives a single argument `article_bs` which is an instance of 
> BeautifulSoup object and returns `None`

Call to this method results in filling the internal Article instance with text.

> NOTE: it is very likely that text on your pages is split across different
> blocks, make sure that you collect all text from the page

# Stage 4. Save article (Stages 0-4 are required to get the mark 4)

Make sure that you save each Article object as a text file on the filesystem by
using the appropriate API method `save_raw`:

```py
article.save_raw()
```

# Stage 5. Collect basic article metadata (Stages 0-5 are required to get the mark 6)

According to the [dataset definition], the dataset that is generated by your code
should contain meta-information about each article: id, title, author.

You should extend ArticleParser with a method `_fill_article_with_meta_information`:

```py
def _fill_article_with_meta_information(self, article_bs):
   pass
```

> NOTE: method receives a single argument `article_bs` which is an instance of 
> BeautifulSoup object and returns `None`

Call to this method results in filling the internal Article instance with meta-information.

> NOTE: if there is no author in your newspaper, contact Dmitry to get help and
> recommendation on possible workarounds.

# Stage 6. Collect advanced metadata: publication date

There is plenty of information that can be collected from each page, much more than title or
author. It is very common to also collect publication date. Working with dates often becomes
a nightmare for a data scientist. It can be very differently represented: `2009Feb17`, 
`2009/02/17`, `20130623T13:22-0500` or even `48/2009` (do you understand what 48 stand for?). 

The task is to ensure that each article metadata is extended with dates. However, the task is
even harder as you have to follow the required format. In particular, you need to translate 
it to the format shown by example: `2021-01-26 07:30:00`. For example, 
[this paper](https://www.nn.ru/text/realty/2021/01/26/69724161/) was
published at `26 ЯНВАРЯ 2021, 07:30` and it should have `2021-01-26 07:30:00` in the 
meta-information. 

> HINT: use `datetime` module for these manipulations. 


> HINT #2: inspect Article class for any possible date transformations


You should extend ArticleParser method `_fill_article_with_meta_information`
with date manipulations.

# Stage 7. Allow several seeds (Stages 0-7 are required to get the mark 8)

As it was stated in Stage 2.1, "Crawler is an entity that visits `seed_urls` with the 
intention to collect URLs with articles that should be parsed later." Often you can
reach the situation when there are not enough article links on the given URL. For example,
you want to collect 100 articles, while each newspaper page has links to only 10 articles. 
This brings the need in several seed URLs to be used for crawling. At this stage
you need to ensure that your Crawler can work with several seeds.

As before, the settings are in the config file. 

However, you need to limit the number of articles that can be retrieved from a single seed.
This setting is specified in the config file under the key 
`max_number_articles_to_get_from_one_seed`.

> IMPORTANT: ensure you have enough seeds in your configuration file to get at least 100 
> articles in your dataset. 100 is a required number of papers for the final part of the
> course.

# Stage 8. Make your crawler a real recursive crawler (Stages 0-8 are required to get the mark 10)

Crawlers used in production or even just for collection of documents from a website should be 
much more robust and tricky than what you have implemented during previous steps. To name
a few challenges:

1. content is not in HTML. Yes, it can happen that your website is an empty HTML by default and
   content appears dynamically when you click, scroll, etc. For example, many pages have 
   so called virtual scroll, when new content appears when you scroll the page. You can think of
   feed in VKontakte, for example.
1. web sites defense against your crawler. Even if data is public, your crawler that sends thousands 
   of requests produces huge load on the server and exposes risks for business continuity. 
   Therefore, websites may reject too many traffic from suspicious origins.
1. there is no way to specify seed URLs - due to size, budget constraints. Imagine, you need
   to collect 100k articles of the Wikipedia. Do you think you are able to copy-paste enough
   seeds? How about the task of collection 1M articles?
1. software and hardware limitations and accidents. Imagine, you have your crawler running for 24 hours
   and it crashes. If you have not mitigated this risk, you lose everything and need to re-start
   your crawler.  

And we are not talking about such objective challenges as impossibility of building universal
crawlers.

Therefore, your stage 8 is about addressing some of these questions. In particular, you need to 
implement your crawler in a recursive manner: you provide a single seed url of your newspaper, and it
visits every page of the website and collects *all* articles from the website. You need to
make a child of `Crawler` class and name it `CrawlerRecursive`. Follow interface of Crawler.

A required addition is an ability to stop crawler at any time. When it is started again, it
continues search and crawling process without repetitions. 

> HINT: think of storing intermediate information in one or few files? What information do you
> need to store?
