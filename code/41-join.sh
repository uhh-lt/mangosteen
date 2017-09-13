#!/bin/bash -xe
# This script works only under GNU join & sort.
# EXTREME BASH POWER GOES HERE
# THE CHALLENGE IS NOT TO PRODUCE INTERMEDIATE FILES
join -t $'\t' --header -j 1 \
  <((head -1 40-wordnet.txt       && tail -n +2        40-wordnet.txt | sort -k1b,1)  | cut -f1-7) \
  <(join -t $'\t' --header -j 1 \
    <(echo -e 'cid\thypernyms'    && sort -k1b,1       30-hypernyms.txt)   \
    <(echo -e 'cid\tsize\tsenses' && sed -e 's/, $//g' 26-cw.txt      | sort -k1b,1)) |
awk 'NR == 1; NR > 1 {print $0 | "sort -t '"'"'\t'"'"' -k6nr -k5nr -k4nr -k3nr -k2nr -k1n"}' >41-join.txt

# <(echo -e 'cid\thypernyms' && cat        30-hypernyms.txt                     | sort -k1b,1)   \
# <(echo -e 'cid\tsenses'    && cut -f1,3  26-cw.txt        | sed -e 's/, $//g' | sort -k1b,1))  |
