#!/usr/bin/env python

# ./31-cluster-gv.py 41

from __future__ import print_function
import sys, os, csv, logging
from collections import Counter, OrderedDict
import networkx as nx
from graphviz import Graph

reload(sys)
sys.setdefaultencoding('utf8')

logging.basicConfig(level=logging.INFO)

if not len(sys.argv) == 2:
    print('Usage: {:s} cid'.format(sys.argv[0]))
    sys.exit(1)

cid = sys.argv[1]

try:
    import cPickle as pickle
except:
    import pickle

import lmdb

DATABASE = os.path.join(os.getcwd(), 'lmdb')

N = 5

prefix_path = os.getenv('PREFIX', 'graphviz')

env = lmdb.open(DATABASE, max_dbs=2, create=False, readonly=True)
senses_db, hypernyms_db = env.open_db('senses'), env.open_db('hypernyms')

cluster = None
senses, hypernyms = {}, {}

with open('26-cw.txt') as f:
    reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in reader:
        if row[0] != cid:
            continue
        cluster = [sense for sense in row[2].split(', ') if sense]
        break

if not cluster:
    logging.critical('Missing CW for %s cluster, skipping', cid)
    sys.exit(1)

with env.begin() as txn:
    for sense in cluster:
        if not sense in senses:
            value = txn.get(sense, db=senses_db)
            if value:
                senses[sense] = pickle.loads(value)
            else:
                logging.warn('No senses for %s', sense)
    value = txn.get(cid, db=hypernyms_db)
    if value:
        hypernyms[cid] = pickle.loads(value)
    else:
        logging.critical('No hypernyms for %s', cid)
        sys.exit(2)

prefix = os.path.join(prefix_path, '31-cluster-' + cid)

G = nx.Graph()
G.add_nodes_from(cluster)

for node1 in G:
    if not node1 in senses:
        continue
    adjacent = [n for n in senses[node1] if n in G and n != node1]
    for node2 in adjacent:
        if node2 not in G[node1]:
            G.add_edge(node1, node2, weight=senses[node1][node2])

logging.info('Graph for %s has %d nodes and %d edges', cid, len(G.nodes()), len(G.edges()))

table_rows = ''.join(['<TR><TD>{:s}</TD><TD>{:f}</TD></TR>'.format(*h) for h in hypernyms[cid].items()])
table = '<TABLE><TR><TD COLSPAN="2"><B>Hypernyms</B></TD></TR>%s</TABLE>' % table_rows
avg_C = nx.average_clustering(G, weight='weight')

gv = Graph(comment='Cluster {:s} for {:s}'.format(cid, ', '.join(hypernyms[cid])), encoding='utf-8', engine='sfdp', format='svg')
gv.body.append('label="Graph for {:s}, average C={:.4f}"'.format(cid, avg_C))
gv.body.append('size="10,10"')
gv.body.append('outputorder=edgesfirst')
gv.body.append('overlap=false')
gv.body.append('splines=true')
gv.node_attr.update(color='#ffffff', margin='0')
gv.edge_attr.update(color='#666666')

gv.node('Legend', label='<{:s}>'.format(table), shape='none', margin='0')
for n in G:
    gv.node(n)

for e1, e2, data in G.edges(data=True):
    gv.edge(e1, e2, weight=str(data['weight']))

if len(G.edges()) > 5000:
    logging.warn('No reason to render such a big graph, so I will not')
    gv_path = gv.save(prefix + '.gv')
    logging.info('Graph is saved: %s', gv_path)
else:
    gv_path = gv.render(prefix + '.gv')
    logging.info('Graph is rendered: %s', gv_path)
