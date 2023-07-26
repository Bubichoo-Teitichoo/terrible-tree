# Tree Tra Trulala

A modern approach to the old tree command. This was born out of pure boredom
and transformed into a useful tool that replaced the plain `tree` command as well
as `ls` on Windows.

## Installation

> ***Note***: There is no pip package available yet so you have to install from
> source.

```shell
# clone this repo
git clone https://github.com/Bubichoo-Teitichoo/tree-tra-trulala
```

```shell
# install the package
pip install "./tree-tra-trulala"
```

## Usage

Here are a few examples how to run this application

```shell
# ls equivalent
treett --depth 1
```

```shell
# maximum depth, no filter, only directories
treett --dirs
```

```shell
# maximum depth of 4, no filter, only directories
treett --dirs --depth 4
```

```shell
# maximum depth of 4, only python files, only directories
treett --dirs --depth 4 -f *.py
```
