#!/usr/bin/env python

from __future__ import print_function
import sys, os, operator, math, csv, logging
from collections import defaultdict
from multiprocessing import Pool

reload(sys)
sys.setdefaultencoding('utf8')
csv.field_size_limit(sys.maxsize)

prefix = sys.argv[1] if len(sys.argv) > 1 else ''

logging.basicConfig(level=logging.INFO)

clusters, bn_synsets = defaultdict(lambda: list()), defaultdict(lambda: set())

with open('50-words.txt') as f:
    reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in reader:
        if row[1]:
            clusters[row[0]].append(row[1])
        if row[2]:
            bn_synsets[row[1]].update(row[2].split(','))

neighbours = defaultdict(lambda: dict())

for line in open('50-neighbours.txt'):
    line = line.rstrip()
    source, targets = line.split('\t', 1)
    for pair in targets.split(','):
        target, level = pair.rsplit(':', 1)
        level = int(level)
        if level > 0:
            neighbours[source][target] = level

def isas(cid):
    cluster = clusters[cid]
    hypernyms = set()

    for i in xrange(0, len(cluster)):
        word_i      = cluster[i]
        synsets_i   = bn_synsets[word_i]
        hypernyms_i = {n: d for s in synsets_i for n, d in neighbours[s].items()}
        others = xrange(0, i) if len(cluster) > 1 else xrange(i, i + 1)
        for j in others:
            word_j      = cluster[j]
            synsets_j   = bn_synsets[word_j]
            hypernyms_j = {n: d for s in synsets_j for n, d in neighbours[s].items()}

            lowest = defaultdict(lambda: set())

            for synset in set(hypernyms_i.keys()) & set(hypernyms_j.keys()):
                cost = math.exp(hypernyms_i[synset]) + math.exp(hypernyms_j[synset])
                lowest[cost].add(synset)

            if len(lowest) > 0:
                hypernyms.update(lowest[min(lowest)])

    return (cid, hypernyms)

logging.info('Processing %d clusters.', len(clusters))

subsumers = set()

with open(os.path.join(prefix, '50-isas.txt'), 'wb') as f:
    writer = csv.writer(f, dialect='excel-tab', lineterminator='\n')
    writer.writerow(('cid', 'hypernyms'))
    pool = Pool(12)
    for cid, hypernyms in pool.imap_unordered(isas, clusters):
        writer.writerow((cid, ','.join(hypernyms)))
        subsumers.update(hypernyms)
    pool.close()

with open(os.path.join(prefix, '50-subsumers.txt'), 'wb') as f:
    for synset in subsumers:
        print(synset, file=f)

logging.info('Done.')
