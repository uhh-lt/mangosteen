#!/bin/bash -ex
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
join -t $'\t' --header -j 1 \
  <(join -t $'\t' --header -j 1 \
    <((head -1 70-cluster-aggregated.tsv  && tail -n +2 70-cluster-aggregated.tsv  | sort -k1b,1) | cut -f1,6-7)  \
    <((head -1 71-hypernym-aggregated.tsv && tail -n +2 71-hypernym-aggregated.tsv | sort -k1b,1) | cut -f1,6-7)) \
  <(head -1 53-join.txt && tail -n +2 53-join.txt | sort -k1b,1) |
$DIR/72-badness.awk >73-join.txt
