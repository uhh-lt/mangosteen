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
        neighbours[source][target] = int(level)

bn_isas = dict()

with open('50-isas.txt') as f:
    reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in reader:
        bn_isas[row[0]] = row[1].split(',')

bn_senses = dict()

with open('51-senses.txt') as f:
    reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in reader:
        bn_senses[row[0]] = {w.rsplit(':', 1)[0].lower() for w in row[1].split(',')}

hypernyms = {}

with open('30-hypernyms.txt') as f:
    reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in reader:
        senses = [kv.split(':', 2) for kv in row[1].split(',')]
        senses = {sense[0]: float(sense[1]) for sense in senses if len(sense) == 2}
        hypernyms[row[0]] = {sense.rsplit('#', 1)[0].lower() for sense in senses}

def evaluate(cid):
    logging.info('Cluster %s started.', cid)

    cluster  = clusters[cid]
    isas     = hypernyms[cid] if cid in hypernyms else set()
    synsets  = {w: bn_synsets[w] for w in cluster if w in bn_synsets}
    coverage = float(len(synsets)) / len(cluster)

    paths = {}
    if len(synsets) > 0:
        for i in xrange(0, len(cluster)):
            word_i = cluster[i]
            if not word_i in synsets:
                continue
            for j in xrange(0, i):
                word_j = cluster[j]
                if not word_j in synsets:
                    continue
                for s1 in synsets[word_i]:
                    for s2 in synsets[word_j]:
                        path = neighbours[s1].get(s2, neighbours[s2].get(s1))
                        if path and ((word_i, word_j) not in paths or path < paths.get((word_i, word_j))):
                            paths[(word_i, word_j)] = abs(path)

    subsumptions = {s for synset in bn_isas[cid] if synset in bn_senses for s in bn_senses[synset]} if cid in bn_isas else set()

    pscore  = sum(paths.values()) / float(len(paths)) if len(paths) > 0 else None
    hscore  = len(subsumptions & isas) / float(len(isas)) if len(isas) > 0 else 0.0
    # npscore = math.log(len(cluster) * coverage, 2) / (1 + pscore) if coverage > 0 and pscore > 0 else None
    hpscore  = (hscore + 1) / (pscore + 1) if pscore else 0.0
    hpcscore = hpscore * coverage

    logging.info('Cluster %s done, coverage is %.4f, p-score is %s, h-score is %f, and hpc-score is %s.',
                 cid, coverage, str(pscore), hscore, hpcscore)
    return (cid, coverage, len(synsets), pscore, hscore, hpscore, hpcscore)

logging.info('Processing %d clusters.', len(clusters))

with open(os.path.join(prefix, '52-babelnet.txt'), 'wb') as f:
    writer = csv.writer(f, dialect='excel-tab', lineterminator='\n')
    writer.writerow(('cid', 'coverage', 'synsets', 'pscore', 'hscore', 'hpscore', 'hpcscore'))
    pool = Pool(12)
    for row in pool.imap_unordered(evaluate, clusters):
        writer.writerow(row)
    pool.close()

logging.info('Done.')
