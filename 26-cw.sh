#!/bin/bash -ex
# Possible cwOption values are TOP, DIST_LOG, and DIST_NOLOG
export LANG=en_US.UTF-8
source params.py
cwOption=${1:-TOP}
java -Xms16G -Xmx16G -cp $PWD/../chinese-whispers/target/chinese-whispers.jar \
     de.tudarmstadt.lt.cw.global.CWGlobal -N 200 -cwOption $cwOption \
     -in '25-pos.txt' -out '26-cw.txt'
