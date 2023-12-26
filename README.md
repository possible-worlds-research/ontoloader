# OntoLoader

**This package is under development. You can take an early peak at your own risk :)**

OntoLoader is a package to extract the logical structure of some world. In its final version, it will provide tools to identify entities, events and situations in a world, as well as associated tagged data and vector representations.


## Installation

We recommend installing this package in a virtual environment. If you do not have virtualenv installed, you can get it in the following way: 

```
sudo apt update
sudo apt install python3-setuptools
sudo apt install python3-pip
sudo apt install python3-virtualenv
```

Then, create a directory for ontoloader, make your virtual environment and install the package:

```
mkdir ontoloader
cd ontoloader
virtualenv env && source env/bin/activate
pip install git+https://github.com/possible-worlds-research/ontoloader.git
```

## Data collection

You will need some data to play with. To get you started, we recommend grabbing some Wikipedia data using the [WikiLoader](https://github.com/possible-worlds-research/wikiloader) package. For instance, let us grab the plots of some action novels to play with:

```
from wikicategories.wikicategories import WikiCatProcessor

lang = 'en'

catprocessor = WikiCatProcessor(lang)

categories = ['Action novels']
catprocessor.get_category_pages(categories)
catprocessor.get_page_content(categories, doctags=False, tokenize=False, lower=False, sections=['Plot'])

```

The corpus we obtain will be saved at *data/en/categories/Action_novels/linear.plot.txt*. It contains the plot summaries of the books tagged as 'Action novel' in Wikipedia.


## Getting character 'bounding boxes'

If you are familiar with 'bounding boxes' from the computer vision literature, you will recognise them as parts of an image that uniquely identify a particular entity. We are expanding the concept here and introduce 'text bounding boxes', which are snippets of text related to a single entity. The snippets have undergone coreference resolution so that the pronouns referring to the entity are resolved in the output.

```
from ontoloader.ontoloader import OntoLoader

ontoloader = OntoLoader()
resolved,idx = ontoloader.coref('data/en/categories/Action_novels/linear.plot.txt')
ontoloader.bounding_box_people(resolved,idx)
```
