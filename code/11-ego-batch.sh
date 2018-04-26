#!/bin/bash -xe
export LANG=en_US.UTF-8
python -m lmdb -S 20480 -e "$PWD/lmdb" drop egos
./lmdb-list.py -0 senses |
xargs -I% -P12 -0 ./10-ego.py '%' 2>10-ego.log
