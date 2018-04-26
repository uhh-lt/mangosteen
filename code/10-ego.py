#!/usr/bin/env python

from __future__ import print_function
import logging, os, sys, csv, tempfile, atexit
from subprocess import check_output

reload(sys)
sys.setdefaultencoding('utf8')

logging.basicConfig(level=logging.INFO)

if not len(sys.argv) == 2:
    print('Usage: {:s} sense'.format(sys.argv[0]))
    sys.exit(1)

sense = sys.argv[1]

try:
    import cPickle as pickle
except:
    import pickle

import lmdb

DATABASE = os.path.join(os.getcwd(), 'lmdb')

CW_JAR = os.path.join(os.getcwd(), 'chinese-whispers', 'target', 'chinese-whispers.jar')

env = lmdb.open(DATABASE, create=False, max_dbs=10, map_size=1024 * 1024 * 1024 * 20)
senses_db, egos_db = env.open_db('senses'), env.open_db('egos')

senses = {}
nodes, edges = {sense}, {}

with env.begin(db=senses_db) as txn:
    value = txn.get(sense)
    if not value:
        logging.warn('Missing sense: %s', node)
        sys.exit()
    senses[sense] = pickle.loads(value)

    nodes.update(senses[sense].keys())
    for node in senses[sense]:
        value = txn.get(node)
        if not value:
            logging.warn('Missing nested sense: %s', node)
            continue
        senses[node] = pickle.loads(value)
        nodes.update(senses[node].keys())

for node1 in nodes:
    if not node1 in senses:
        continue
    adjacent = [n for n in senses[node1] if n in nodes and n != node1]
    for node2 in adjacent:
        if not (node2, node1) in edges:
            edges[(node1, node2)] = senses[node1][node2]

undirected = []

for (e1, e2), w in edges.items():
    undirected.append((e1, e2, w))
    undirected.append((e2, e1, w))

fd_input, cw_input_path = tempfile.mkstemp()
atexit.register(lambda: os.remove(cw_input_path))

for edge in sorted(undirected):
    os.write(fd_input, '{:s}\t{:s}\t{:f}\n'.format(*edge))

os.close(fd_input)

fd_output, cw_output_path = tempfile.mkstemp()
atexit.register(lambda: os.remove(cw_output_path))

invocation = [
    '/usr/bin/java', '-Xms4G', '-Xmx4G',
    '-cp', CW_JAR, 'de.tudarmstadt.lt.cw.global.CWGlobal',
    '-N', '200',
    '-cwOption', 'TOP',
    '-in', cw_input_path,
    '-out', cw_output_path
]

check_output(invocation)

cws = {}

with open(cw_output_path) as f:
    reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
    for row in reader:
        cws[int(row[0])] = {s for s in row[2].split(', ') if s}

os.close(fd_output)

with env.begin(db=egos_db, write=True) as txn:
    txn.put(sense, pickle.dumps(cws))
