Mangosteen
==========

About the method
----------------

Mangosteen is a rare fruit. This repository contains an implementation of a a system for inducing distributional sense-aware semantic classes labeled with hypernyms. It helps to induced hypernyms of rare words, such as "mangosteen", which are often cannot be directly extracted from text, because such rare words do not appear in the required for extraction contexts. The method implemented in this repository was presented at the LREC'2018 conference in Miyazaki, Japan. [The paper is available online (PDF)](https://arxiv.org/abs/1711.02918). Please use the following cite to refer to this work:

```
@inproceedings{Panchenko:18:lrec,
  author    = {Alexander Panchenko, Dmitry Ustalov, Stefano Faralli, Simone P. Ponzetto, Chris Biemann},
  title     = {{Improving Hypernymy Extraction with Distributional Semantic Classes}},
  year      = {2018},
  url       = {https://arxiv.org/abs/1711.02918},
  booktitle = {Proceeding of the 11th Language Resource and Evaluation Conference (LREC'2018)},
  address   = {Miyazaki, Japan},
  publisher = {ELRA},
  language  = {english},
}
```

In this paper, we show how distributionally-induced semantic classes can be helpful for extracting hypernyms. We present methods for inducing sense-aware semantic classes using distributional semantics and using these induced semantic classes for filtering noisy hypernymy relations. Denoising of hypernyms is performed by labeling each semantic class with its hypernyms. On the one hand, this allows us to filter out wrong extractions using the global structure of distributionally similar senses. On the other hand, we infer missing hypernyms via label propagation to cluster terms. We conduct a large-scale crowdsourcing study showing that processing of automatically extracted hypernyms using our approach improves the quality of the hypernymy extraction in terms of both precision and recall. Furthermore, we show the utility of our method in the domain taxonomy induction task, achieving the state-of-the-art results on a SemEval'16 task on taxonomy induction


Structure of the repository
---------------------------

This repository contains databases of hypernyms cleansed and expanded with our method. The result of the extraction is available in the directory ```data```, while the scripts are available in the directory ```code```. The cleansed hypernymy relations extracted with the coarse model are [available online](https://docs.google.com/spreadsheets/d/1g8aCVm6SozuHyBmld-X69bDdek1gzBvQfu7wJJv1b8U/edit?usp=sharing). 

The input and output datasets used in the experiment can be downloaded [here](https://zenodo.org/record/1174041#.Wob1m2aZMWo). The Wikipedia dump used to induce word senses can be downloaded [here](https://zenodo.org/record/229904#.Wob4OmaZMWo).

![mangosteen](https://media.mercola.com/assets/images/foodfacts/mangosteen-fb.jpg)
Image source: https://media.mercola.com/assets/images/foodfacts/mangosteen-fb.jpg
