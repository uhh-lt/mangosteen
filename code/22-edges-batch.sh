#!/bin/bash -ex
# This script works only under GNU sort.
export LANG=en_US.UTF-8
source params.py
./20-edges.py 2>20-edges.log >20-edges.txt
LC_ALL=C sort --parallel=8 -s 20-edges.txt |
./21-count.awk >22-edges.txt
