#!/bin/bash -ex
# This script works only under GNU sort.
export LANG=en_US.UTF-8
source params.py
awk -v T=$T -v E=$E -f ./23-prune.awk <22-edges.txt |
LC_ALL=C sort --parallel=8 -s >24-prune.txt
