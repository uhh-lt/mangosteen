# Mangosteen, the Implementation of

This is the source code for the Mangosteen approach described in the paper “[Improving Hypernymy Extraction with Distributional Semantic Classes](https://arxiv.org/abs/1711.02918)”.

## Parameters

Mangosteen has five parameters:

* `P`, the threshold for the ego network size proportion, this is a real number,
* `T`, the edge weight threshold in co-occurence graphs, this is a real number,
* `E`, the edge weighting approach, can be either `count` or `log`,
* `N`, the flag for noun filtering, can be either `0` (no) and `1` (yes),
* `H`, the hypernym weighting approach, can be either `tf` or `tfidf`.

For interoperability purposes, the `params.py` is, in fact, a Bash script to share parameters between the shell and Python scripts. It is automatically generated from the template file: `params.py.txt`.

## Pipeline

Mangosteen takes a *disambiguated distributional thesaurus* (DDT) as an input and outputs a set of disambiguated semantic classes, each class is additionally provided with a set of disambiguated hypernyms. It has four steps:

1. Clustering ego networks (Section 3.2 of the [paper])
2. Constructing and clustering a global graph (Sections 3.3 & 3.4 of the [paper])
3. Gathering and disambiguation the hypernyms (Section 4 of the [paper])
4. Parameter tuning (Section 5 of the [paper])

The input file is a text file containing tab-separated values with header:

|word|cid|cluster|isas|
|----|---|-------|----|
|cat|0|`dog#2:0.255,rabbit#0:0.215,kitten#0:0.210`|`animal#0:24.501,wildlife#0:5.885,mammal#0`|
|kitten|0|`cat#0:0.210,puppy#0:0.175,dog#2:0.139`|`animal#0:9.875,wildlife#0:1.774,mammal#0:1.718`|

The `word` column contains lexical entries. The `cid` column contains sense identifiers of these entries. The `cluster` column contains comma-separated related word senses with weights. The `isas` column contains comma-separated upper word sense with weights.

## Code Structure

Mangosteen is implemented in a UNIX-way. It is pipeline-based. It runs small different programs written in different languages to achieve the goal of semantic class induction. There are the following programs:

### Necessary Preparations

* `00-convert.py` imports a DDT into an embedded database [LMDB](https://symas.com/lmdb/).

### Clustering Ego Networks

* `10-ego.py` extracts ego networks (node neigborhoods) and clusters each of them using [Chinese Whispers] (it takes quite a long time);
* `11-ego-batch.sh` cleans up the `egos` table in LMDB and runs `10-ego.py` with logging.

### Constructing and Clustering a Global Graph

* `20-edges.py` unions all the clusters ego networks into a global graph, no weights assigned;
* `21-count.awk` counts the number of edge appearance and assigns count-based weights to the edges of the global graph;
* `22-edges-batch.sh` subsequently runs `20-edges.py` and `21-count.awk` with parallel sorting;
* `23-prune.awk` removes the edges with the weight smaller than `T` and optionally does a log-transform of the weights;
* `24-prune-batch.sh` runs `23-prune.awk` with parallel sorting;
* `25-pos.py` optionally keeps the nouns and multi-word expressions only;
* `26-cw.sh` runs [Chinese Whispers] on the weighted pruned global graph to obtain semantic classes.

### Gathering and Disambiguation the Hypernyms

* `30-isas.py` induces hypernyms for the obtained semantic classes.

### Visualization

* `31-cluster-gv.py` draws a semantic class with [Graphviz](https://www.graphviz.org/);
* `32-isas-gv.py` draws hypernyms for a semantic class with [Graphviz](https://www.graphviz.org/);
* `33-isas-gephi.py` writes the global graph in the [Gephi](https://gephi.org/) format;
* `arrange.sh` moves the present results into a separate directory and produces graphs for the words *python*, *ruby*, and *java* using `31-cluster-gv.py` and `32-isas-gv.py` and also writes the global graph using `33-isas-gephi.py`.

### Parameter Tuning

* `40-wordnet.py` computes hpc-score on the Princeton WordNet;
* `41-join.py` joins the obtained semantic classes with the evaluation results from `40-wordnet.py`;
* `51-clusters.sh` extracts the synsets from BabelNet;
* `52-babelnet.py` computes hpc-score on BabelNet;
* `53-join.sh` joins the obtained semantic classes with the evaluation results from `52-babelnet.py`;
* `aggregate.awk` summarizes the evaluation results from `40-wordnet.py` and/or `52-babelnet.py`;
* `enumerate.sh` enumerates over all the parameter combinations defined in the script.

## Usage

The reader is probably shocked by the amount of scripts above. Please do not worry. We offer a *very convenient* `Makefile` that does everything automatically:

* `make chinese-whispers` installs the [Chinese Whispers] dependency;
* `make babelnet-extract` installs the [BabelNet Extract](https://github.com/nlpub/babelnet-extract) dependency and extracts the useful data from it (it takes quite a long time);
* `make egos` obtains clusters ego networks;
* `make clusters` obtains semantic classes with hypernyms;
* `make arrange` writes the summaries using `enumerate.sh`;
* `make evaluate` tunes the parameters using `enumerate.sh`.

The name of the input file is expected to be `ddt.tsv` which can be downloaded [here](http://panchenko.me/data/joint/ddt/ddt-mwe-45g-8m-thr-agressive2-cw-e0-N200-n200-minsize5-isas-cmb-nopos-closure.csv.gz) or via `make ddt.tsv`. Generally, to reproduce our study, it is sufficient to run `make all` after installing the dependencies. All the resulting files are stored in the dictionary named like `P80_T100_Elog_N0_Htfidf`. The directory name reflects the parameters used to obtain the results. The following files can be of interest:

* `41-join.txt` with the semantic classes, their hyperyms, and WordNet-based scores;
* `42-aggregate.txt` with the summary on the evaluation on WordNet;
* `53-join.txt` with the semantic classes, their hyperyms, and BabelNet-based scores.
* `54-aggregate.txt` with the summary on the evaluation on BabelNet;

## Remarks

We used Debian Linux 8 (Jessie), the [Anaconda](https://www.anaconda.com/download/) distribution of Python 2, and Java 8. We cannot guarantee compatibility with other systems.

[paper]: https://arxiv.org/abs/1711.02918
[Chinese Whispers]: (https://github.com/uhh-lt/chinese-whispers)
