#!/usr/bin/env python

from __future__ import print_function
import sys, os, operator, math, csv, logging
from nltk.corpus import wordnet as wn, wordnet_ic
from nltk.corpus.reader.wordnet import WordNetError
from multiprocessing import Pool

reload(sys)
sys.setdefaultencoding('utf8')

prefix = sys.argv[1] if len(sys.argv) > 1 else ''

logging.basicConfig(level=logging.INFO)

clusters = {}

with open(os.path.join(prefix, '26-cw.txt')) as f:
    reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in reader:
        cid, senses = row[0], [sense for sense in row[2].split(', ') if sense]
        clusters[cid] = [sense.rsplit('#', 1)[0] for sense in senses]

hypernyms = {}

with open('30-hypernyms.txt') as f:
    reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in reader:
        senses = [kv.split(':', 2) for kv in row[1].split(',')]
        senses = {sense[0]: float(sense[1]) for sense in senses if len(sense) == 2}
        hypernyms[row[0]] = {sense.rsplit('#', 1)[0].lower() for sense in senses}

brown_ic = wordnet_ic.ic('ic-brown.dat')

def evaluate(cid):
    logging.info('Cluster %s started.', cid)

    cluster  = clusters[cid]
    isas     = hypernyms[cid] if cid in hypernyms else set()
    synsets  = {w: wn.synsets(w) for w in cluster if wn.synsets(w)}
    coverage = float(len(synsets)) / len(cluster)

    paths, jcns, ress, subsumptions = {}, {}, {}, set()
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
                        # p-score computation
                        path = s1.shortest_path_distance(s2, True)
                        if path and ((word_i, word_j) not in paths or path < paths.get((word_i, word_j))):
                            paths[(word_i, word_j)] = path

                        # h-score computation
                        lch = s1.lowest_common_hypernyms(s2, use_min_depth=True)
                        if not lch:
                            # This usually happens when a noun synset is
                            # checked against a verb synset, or vice versa.
                            continue
                        lemmas = reduce(operator.add, [s.lemma_names() for s in lch])
                        subsumptions.update({w.lower().replace('_', ' ') for w in lemmas})

    pscore   = sum(paths.values()) / float(len(paths)) if len(paths) > 0 else None
    # npscore   = math.log(len(cluster) * coverage, 2) / (1 + pscore) if coverage > 0 and pscore > 0 else None

    hscore   = len(subsumptions & isas) / float(len(isas)) if len(isas) > 0 else 0.0
    hpscore  = (hscore + 1) / (pscore + 1) if pscore else 0.0
    hpcscore = hpscore * coverage

    logging.info('Cluster %s done, coverage is %.4f, p-score is %s, h-score is %f, and hpc-score is %s.',
                 cid, coverage, str(pscore), hscore, hpcscore)
    return (cid, coverage, len(synsets), pscore, hscore, hpscore, hpcscore)

logging.info('Processing %d clusters.', len(clusters))

with open(os.path.join(prefix, '40-wordnet.txt'), 'wb') as f:
    writer = csv.writer(f, dialect='excel-tab', lineterminator='\n')
    # writer.writerow(('cid', 'coverage', 'synsets', 'pscore', 'npscore', 'jcnscore', 'njcnscore', 'resscore', 'nresscore', 'hypernyms', 'hscore'))
    writer.writerow(('cid', 'coverage', 'synsets', 'pscore', 'hscore', 'hpscore', 'hpcscore'))
    pool = Pool(12)
    for row in pool.imap_unordered(evaluate, clusters):
        writer.writerow(row)
    pool.close()

logging.info('Done.')
