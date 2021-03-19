# Process raw data

> Python competencies required to complete this tutorial:
> * working with external dependencies, going beyond Python standard library
> * working with external modules: local and downloaded from PyPi
> * working with files: create/read/update
> * applying basic cleaning techniques to the raw text: tokenization, lemmatization
> * extracting linguistic data from the raw text: part of speech and its attributes

Processing data as a process contains following steps:
1. loading raw data
1. tokenizing the text
1. performing necessary transformations, such as lemmatization or stemming, and extract 
   valuable information from the text, such as detect each word part of speech.
1. saving necessary information

As a part of the second milestone, you need to implement processing logic as a `pipeline.py` module.
When it is run as a standalone Python program, it should perform all aforementioned stages.

## Executing pipeline

Example execution (`Windows`):

```bash
py pipeline.py
```

Expected result:
1. `N` raw texts collected as a result of scrapping are processed
1. each article has a processed version saved in the `tmp/articles` directory. `tmp` directory content:
```
+-- 2020-2-level-ctlr
    +-- tmp
        +-- articles
            +-- 1_raw.txt <- the paper with the ID as the name
            +-- 1_meta.json <- the paper meta-information
            +-- 1_processed.txt <- the tokenized, lemmatized, tagged paper text 
```

> NOTE: When using CI (Continuous Integration), generated `dataset.zip` is available in
> build artifacts. Go to `Actions` tab in GitHub UI of your fork, open the last job and
> if there is an artifact, you can download it.

## Configuring pipeline

Processing behaviour is not configurable:

1. pipeline takes a raw dataset that is collected by
   `crawler.py` and placed at `ASSETS_PATH` (see `constants.py` for a particular place)
1. pipeline goes through each raw file, for example `1_raw.txt`
1. pipeline performs tokenization, lemmatization and morphological analysis of the text
1. resulting text with morphological tags is saved to a processed file, for example `1_processed.txt`

## Assessment criteria

You state your abmitions on the mark by editing the file `target_score.txt` at the `line 5`. For example, such content:
```
...
# Target score for pipeline.py:
6
```
would mean that you have made tasks for mark `6` and request mentors to check if you can get it.

1. Desired mark: **4**:
   1. pylint level: `5/10`
   1. scrapper validates that raw dataset has a proper structure and fails appropriately if the latter is incorrect.
      Criteria:
        1. dataset exists (there is a folder)
        1. dataset is not empty (there are files inside)
        1. dataset is balanced: there are only files that follow the naming conventions:
            1. `N_raw.txt`, `N_meta.json`, where N is a valid number
            1. Numbers of articles are from 1 to N without any slips
   1. pipeline tokenizes text in each file, removes punctuation,
      and casts it to the lower case (*no lemmatization or tagging*)
      Example raw text: [config/test_files/0_raw.txt](./config/test_files/0_raw.txt). 
      Desired output: 
      [config/test_files/reference_score_four_test.txt](./config/test_files/reference_score_four_test.txt)
   1. pipeline produces only `N_processed.txt` files in the `tmp/articles`
1. Desired mark: **6**:
   1. pylint level: `7/10`
   1. all requirements for the mark **4**
   1. pipeline produces `N_processed.txt` files for each article, where each word is lemmatized and has
      a properly formatted tag.
      Example raw text: [config/test_files/0_raw.txt](./config/test_files/0_raw.txt). 
      Desired output: 
      [config/test_files/reference_test.txt](./config/test_files/reference_test.txt).
    1. pipeline uses pymystem library to perform lemmatization and tagging (more details in the description below) 
    1. pymystem tags are represented in angle brackets (within this tutorial we refer to it as a **pymystem-format**)
1. Desired mark: **8**:
   1. pylint level: `10/10`
   1. all requirements for the mark **6**
   1. pipeline additionally uses pymorphy2 library to perform tagging (more details in the description below)
   1. pymorphy2 tags are represented in brackets (within this tutorial we refer to it as a **pymorphy2-format**)
1. Desired mark: **10**:
   1. pylint level: `10/10`
   1. all requirements for the mark **8**
   1. an additional pipeline is introduced `pos_pipeline.py` that:
      1. collects frequencies of parts of speech in each text
      1. extends `_meta.json` files with this information
      1. visualizes this distribution as png files that are created for each article
         and saved into `N_image.png` files

## Implementation tactics

> NOTE: all logic that instantiates needed abstractions and uses them should be implemented
> on the module level of the `pipeline.py`, in a special block
```py
def main():
    print('Your code goes here')

if __name__ == '__main__':
    main()
```

### Stage 0. Ensure scrapper.py is working

You will not be able to start your implementation if there is no collected dataset.
Dataset is collected by scrapper.py. Therefore, if you still do not have it working,
fix all the issues. Healthcheck would be existence of a raw dataset in the `tmp/articles`
folder on your computer. For more details on how to implement `scrapper.py` refer to the 
[scrapper tutorial](./scrapper.md).

### Stage 1. Validate dataset first

Pipeline expects that dataset is collected and even do not start working if it is not valid.
Very first thing that should happen after pipeline is run is validation of the dataset.

Interface to implement:

```py
def validate_dataset(dataset_path):
    pass
```

`dataset_path` is the path to the dataset. It is mandatory to call this
method with passing a global variable `ASSETS_PATH` that should be properly
imported from the `constants.py` module.

Example call:

```py
validate_dataset(ASSETS_PATH)
```

When dataset is valid, method returns `None`.

When dataset is not valid:

1. one of the following errors is thrown (names of 
   errors are self-explaining):
   `FileNotFoundError`, `NotADirectoryError`, `InconsistentDatasetError`,
   `EmptyDirectoryError`, and throw `UnknownDatasetError` if
   any other inconsstency is found.
2. script immediately finishes execution
