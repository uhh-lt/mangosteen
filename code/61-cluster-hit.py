#!/usr/bin/env python

from __future__ import print_function
import sys, os, operator, math, csv, logging, random, re
from collections import defaultdict, namedtuple
from multiprocessing import Pool

reload(sys)
sys.setdefaultencoding('utf8')
csv.field_size_limit(sys.maxsize)

prefix = sys.argv[1] if len(sys.argv) > 1 else ''

logging.basicConfig(level=logging.INFO)

try:
    import cPickle as pickle
except:
    import pickle

SENSES    = 5  # the number of original senses sampled per HIT
HYPERNYMS = 3  # the number of top hypernyms per HIT
WINDOW    = 10 # the width of the side of the frequency window

Cluster = namedtuple('Cluster', 'cid senses hypernyms')

# is_word = re.compile(r"\A(?P<word>([\w'-]+ {0,1} *)+)\Z")

with open('60-frequencies.pickle', 'rb') as f:
    freqs = pickle.load(f)
    freqs_keys = freqs.keys()

stopwords = set()

with open('ddt.tsv') as f:
    reader = csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in reader:
        stopwords.add(row['word'].lower())

        if row['cluster']:
            stopwords.update({kv.split(':', 2)[0].rsplit('#', 1)[0].lower() for kv in row['cluster'].split(',')})

        if row['isas']:
            stopwords.update({kv.split(':', 2)[0].rsplit('#', 1)[0].lower() for kv in row['isas'].split(',')})

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
        else:
            logging.warn('Cluster %s has only %d sense(s), skipping.', cid, len(senses))

def emit(cid):
    cluster = clusters[cid]

    senses = list({w.lower() for w in cluster.senses})
    random.shuffle(senses)
    senses = senses[:SENSES]
    logging.info('Starting cluster %s: %s.', cid, ', '.join(senses))

    try:
        mfw, _ = max(((w, freqs[w]) for w in senses if w in freqs), key=operator.itemgetter(1))
    except ValueError:
        logging.warn('Neither word of cluster %s present in the concordance, skipping.', cid)
        return

    mfw_index = freqs_keys.index(mfw)

    generator = ((freqs_keys[i], freqs[freqs_keys[i]])
                 for i in xrange(mfw_index - WINDOW, mfw_index + WINDOW + 1)
                 if freqs_keys[i].lower() not in senses
                 and freqs_keys[i].lower() not in stopwords
                 # Thank you, Python, for a very efficient regexp engine. Not.
                 # and is_word.match(freqs_keys[i]))
                 and '-' not in freqs_keys[i]
                 and '_' not in freqs_keys[i]
                 and '`' not in freqs_keys[i]
                 and '"' not in freqs_keys[i]
                 and ',' not in freqs_keys[i]
                 and ';' not in freqs_keys[i]
                 and ':' not in freqs_keys[i]
                 and '/' not in freqs_keys[i]
                 and '(' not in freqs_keys[i]
                 and ')' not in freqs_keys[i]
                 and '{' not in freqs_keys[i]
                 and '}' not in freqs_keys[i]
                 and '[' not in freqs_keys[i]
                 and ']' not in freqs_keys[i])
    try:
        intruder, _ = generator.next()
    except StopIteration:
        logging.warn('No intruders found for cluster %s, skipping.', cid)
        return

    intruder = intruder.lower()
    senses.append(intruder)
    random.shuffle(senses)
    intruder_index = senses.index(intruder)

    row = [cid, senses.index(intruder) + 1]
    for i in xrange(SENSES + 1):
        if len(senses) > i:
            row.append(senses[i])
        else:
            row.append(None)
    for i in xrange(HYPERNYMS):
        if len(cluster.hypernyms) > i:
            row.append(cluster.hypernyms[i])
        else:
            row.append(None)
    logging.info('Emitted a task for cluster %s with %d senses.', cid, len(senses))
    return row

with open(os.path.join(prefix, '61-cluster-hit.tsv'), 'wb') as f:
    writer = csv.writer(f, dialect='excel-tab', lineterminator='\n')

    row = ['cid', 'intruder']
    for i in xrange(SENSES + 1):
        row.append('sense%d' % (i + 1))
    for i in xrange(HYPERNYMS):
        row.append('hypernym%d' % (i + 1))
    writer.writerow(row)

    pool = Pool(12)
    for row in pool.imap_unordered(emit, clusters):
        if row:
            writer.writerow(row)
    pool.close()

logging.info('Done.')
