#!/usr/bin/env python

# ./34-isas-gephi.py

from __future__ import print_function
import sys, csv, logging, itertools
from collections import defaultdict
import networkx as nx

reload(sys)
sys.setdefaultencoding('utf8')

logging.basicConfig(level=logging.INFO)

try:
    import cPickle as pickle
except:
    import pickle

import lmdb

DATABASE = '/home/dmitry/lmdb'

env = lmdb.open(DATABASE, max_dbs=1, create=False, readonly=True)
hypernyms_db = env.open_db('hypernyms')

clusters, index = {}, {}

with open('26-cw.txt') as f:
    reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in reader:
        cid = row[0]
        clusters[cid] = [sense for sense in row[2].split(', ') if sense]
        for sense in clusters[cid]:
            index[sense] = cid

hypernyms = {}

with env.begin(db=hypernyms_db) as txn:
    for cid in clusters:
        value = txn.get(cid)
        if value:
            hypernyms[cid] = pickle.loads(value)
        else:
            logging.warn('No hypernyms for cluster %s', cid)
            hypernyms[cid] = {}

G = nx.Graph()

for cid, isas in hypernyms.items():
    label = '{:s}: {:s}'.format(cid, ', '.join(isas))
    G.add_node(cid, label=label)

logging.info('Nodes: %d', len(G.nodes()))

with open('25-pos.txt') as f:
    reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in reader:
        n1, n2 = index[row[0]], index[row[1]]
        G.add_edge(n1, n2)

logging.info('Edges: %d', len(G.edges()))

with open('33-nodes.csv', 'wb') as f:
    writer = csv.writer(f, dialect='excel-tab', lineterminator='\n')
    writer.writerow(('id', 'label'))
    for n, data in G.nodes(data=True):
        writer.writerow((n, data['label']))

with open('33-edges.csv', 'wb') as f:
    writer = csv.writer(f, dialect='excel-tab', lineterminator='\n')
    writer.writerow(('source', 'target'))
    for n1, n2, data in G.edges(data=True):
        writer.writerow((n1, n2))
