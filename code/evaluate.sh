#!/bin/bash -ex

export LANG=en_US.UTF-8

P=$(printf '%.0f' $(bc -q <<< "$P*100"))
TARGET="P$P""_T$T""_E$E""_N$N""_H$H"

cd $TARGET

rm -f 42-aggregate.txt 54-aggregate.txt

if [ -f '54-aggregate.txt' ]; then
    echo "$TARGET already has 54-aggregate.txt"
    exit
fi

../40-wordnet.py
../41-join.sh >41-join.txt
../aggregate.awk <41-join.txt >42-aggregate.txt

# If the BABELNET_EVAL flag is not set, we are done.
if [ -z ${BABELNET_EVAL+x} ]; then
    exit
fi

# ../51-clusters.sh
../52-babelnet.py
../53-join.sh >53-join.txt
../aggregate.awk <53-join.txt >54-aggregate.txt
