#!/usr/bin/env python

from __future__ import print_function
import sys, os, operator, math, csv, json, logging, random, re
from collections import defaultdict, namedtuple, Counter

reload(sys)
sys.setdefaultencoding('utf8')
csv.field_size_limit(sys.maxsize)

prefix = sys.argv[1] if len(sys.argv) > 1 else ''

logging.basicConfig(level=logging.INFO)

Cluster = namedtuple('Cluster', 'cid senses hypernyms')

clusters = {}

with open(os.path.join(prefix, '53-join.txt')) as f:
    reader = csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in reader:
        cid = row['cid']

        senses = [sense for sense in row['senses'].split(', ') if sense]
        senses = [sense.rsplit('#', 1)[0] for sense in senses]

        hypernyms = [kv.split(':', 2) for kv in row['hypernyms'].split(',')]
        hypernyms = {(hypernym[0], float(hypernym[1])) for hypernym in hypernyms if len(hypernym) == 2}
        hypernyms = [w.rsplit('#', 1)[0].lower() for w, _ in sorted(hypernyms, key=operator.itemgetter(1), reverse=True)]

        if len(senses) > 2:
            clusters[cid] = Cluster(cid, senses, hypernyms)

filtered, total = 0, 0

with open(os.path.join(prefix, '61-cluster-hit.tsv')) as f:
    reader = csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in reader:
        cid = row['cid']
        lower = Counter([str.islower(sense[0]) for sense in clusters[cid].senses]).most_common(1)[0][0]
        if not lower:
            print((cid, clusters[cid].senses, clusters[cid].hypernyms))
            filtered += 1
        total += 1

logging.info('%d out of %d clusters have been filtered.', filtered, total)

# from IPython import embed; embed()
