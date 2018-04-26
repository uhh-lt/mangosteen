#!/bin/bash -ex
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CWD=$PWD
(
  cd $CWD/babelnet-extract
  java -Xms32G -Xmx32G -jar target/babelnet-extract.jar \
    -action synsets -clusters "$CWD/26-cw.txt" -words "$CWD/50-words.txt" -synsets "$CWD/50-synsets.txt"
  java -Xms32G -Xmx32G -jar target/babelnet-extract.jar \
    -action neighbours -synsets "$CWD/50-synsets.txt" -neighbours "$CWD/50-neighbours.txt" -depth 2
)
$DIR/50-bn-isas.py
(
  cd $CWD/babelnet-extract
  java -Xms32G -Xmx32G -jar target/babelnet-extract.jar \
    -action senses -synsets "$CWD/50-subsumers.txt" -senses "$CWD/51-senses.txt"
)
