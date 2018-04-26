# Mangosteen, the Implementation of

This is the source code for the Mangosteen approach described in the paper “[Improving Hypernymy Extraction with Distributional Semantic Classes](https://arxiv.org/abs/1711.02918)”.

## Parameters

Mangosteen has five parameters:

* `P`, the threshold for the ego network size proportion, this is a real number,
* `T`, the edge weight threshold in co-occurence graphs, this is a real number,
* `E`, the edge weighting approach, can be either `count` or `log`,
* `N`, the flag for noun filtering, can be either `0` (no) and `1` (yes),
* `H`, the hypernym weighting approach, can be either `tf` or `tfidf`.

For interoperability purposes, the `params.py` is, in fact, a Bash script to share parameters between the shell and Python scripts.

## Pipeline

Mangosteen takes a *disambiguated distributional thesaurus* (DDT) as an input and outputs a set of disambiguated semantic classes, each class is additionally provided with a set of disambiguated hypernyms. It has five steps:

1. Importing the DDT into an embedded database (LMDB)
2. Clustering ego networks (Section 3.2 of the paper)
3. Constructing and clustering a global graph (Sections 3.3 & 3.4 of the paper)
4. Gathering and disambiguation the hypernyms (Section 4 of the paper)
5. Parameter tuning (Section 5 of the paper)

## Importing the DDT into an embedded database (LMDB)

## Clustering ego networks

## Constructing and clustering a global graph

## Gathering and disambiguation the hypernyms

## Parameter tuning

## Remarks

We used Debian Linux and the [Anaconda](https://www.anaconda.com/download/) distribution of Python 2. We cannot guarantee compatibility with other systems.

[paper]: https://arxiv.org/abs/1711.02918
