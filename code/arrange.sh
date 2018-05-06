#!/bin/bash -ex

envsubst <params.py.txt >params.py
rm -fv params.pyc
make clusters

export LANG=en_US.UTF-8
source params.py

P=$(printf '%.0f' $(bc -q <<< "$P*100"))
TARGET="P$P""_T$T""_E$E""_N$N""_H$H"
echo $TARGET

trap "rm -rf \"$TARGET\" \"graphviz\"" INT

rm -rf "$TARGET" "graphviz"
mkdir -p "$TARGET" "graphviz"

cp -fv "params.py" "26-cw.txt" "30-hypernyms.txt" "$TARGET/"

set +e
egrep -i '(python|ruby|jaguar)' 26-cw.txt | cut -f1 | xargs -n1 -P8 -t ./31-cluster-gv.py
set -e

# set +e
# cut -f1 26-cw.txt | xargs -n1 -P12 -t ./31-cluster-gv.py
# echo $?
# cp -fv "31-cluster-gv.log" "$TARGET/"
# set -e

set +e
sed -nre 's/^(python|ruby|jaguar)\t([[:digit:]]+).*/\1#\2/gpi' ddt.tsv | xargs -t ./32-isas-gv.py
set -e

./33-isas-gephi.py
cp -fv "33-nodes.csv" "33-edges.csv" "$TARGET/"

mv -fv "graphviz" "$TARGET/"
