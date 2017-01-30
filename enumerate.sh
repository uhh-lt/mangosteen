#!/bin/bash -ex
for P in 0.8; do
for T in 0 10 100; do
for E in count log; do
for N in 0 1; do
for H in tf tfidf; do
  export P T E N H
  echo "# P=$P T=$T E=$E N=$N H=$H"
  $@
done
done
done
done
done
