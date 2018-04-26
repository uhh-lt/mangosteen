#!/usr/bin/env python

# ./32-isas-gv.py Ruby#1 Python#3

from __future__ import print_function
import sys, os, csv, logging, itertools
from collections import defaultdict
import networkx as nx
from graphviz import Graph

reload(sys)
sys.setdefaultencoding('utf8')

logging.basicConfig(level=logging.INFO)

if len(sys.argv) < 2:
    print('Usage: {:s} sense(s)'.format(sys.argv[0]))
    sys.exit(1)

prefix_path = os.getenv('PREFIX', 'graphviz')
senses = {sense: None for sense in sys.argv[1:]}

try:
    import cPickle as pickle
except:
    import pickle

import lmdb

DATABASE = os.path.join(os.getcwd(), 'lmdb')

env = lmdb.open(DATABASE, max_dbs=2, create=False, readonly=True)
senses_db, hypernyms_db = env.open_db('senses'), env.open_db('hypernyms')

clusters = {}

with open('26-cw.txt') as f:
    reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in reader:
        cid = row[0]
        csenses = [sense for sense in row[2].split(', ') if sense]
        intersection = set(senses) & set(csenses)
        for sense in intersection:
            senses[sense] = cid
            clusters[cid] = csenses

hypernyms = {}

with env.begin(db=hypernyms_db) as txn:
    for cid in clusters:
        value = txn.get(cid)
        if value:
            hypernyms[cid] = pickle.loads(value)
        else:
            logging.warn('No hypernyms for cluster %s', cid)

index = defaultdict(lambda: set())

for cid, cluster_senses in clusters.items():
    for sense in cluster_senses:
        index[sense].add(cid)

with env.begin(db=senses_db) as txn:
    for sense, cids in index.items():
        value = txn.get(sense)
        if not value:
            logging.warn('Missing sense: %s', sense)
            continue
        for neighbour in pickle.loads(value):
            if neighbour in index:
                cids.update(index[neighbour])
                index[neighbour].update(cids)

prefix = os.path.join(prefix_path, '32-isas-' + '_'.join(s for s in senses.values() if s))

G = nx.Graph()

for cid, isas in hypernyms.items():
    table_rows = ''.join(['<TR><TD>{:s}</TD><TD>{:.2f}</TD></TR>'.format(*s) for s in isas.items()])
    table = '<TABLE><TR><TD COLSPAN="2"><B>{:s}</B></TD></TR>{:s}</TABLE>'.format(cid, table_rows)
    G.add_node(cid, label='<{:s}>'.format(table))

for nodes in index.values():
    for n1, n2 in itertools.combinations(nodes, 2):
        G.add_edge(n1, n2)

table_rows = ''.join(['<TR><TD>{:s}</TD><TD>{:s}</TD></TR>'.format(*s) for s in sorted(senses.items())])
table = '<TABLE><TR><TD><B>Sense</B></TD><TD><B>Cluster</B></TD></TR>{:s}</TABLE>'.format(table_rows)

gv = Graph(comment='Cluster', encoding='utf-8', engine='circo', format='svg')
gv.body.append('size="10,10"')
gv.body.append('outputorder=edgesfirst')
gv.body.append('overlap=false')
gv.body.append('splines=true')
gv.node_attr.update(color='#228322', shape='rectangle')
gv.edge_attr.update(color='#031337')

gv.node('Legend', label='<{:s}>'.format(table), shape='none', margin='0', color='#000000')
for n, data in G.nodes(data=True):
    gv.node(n, label=data['label'])

for e1, e2, data in G.edges(data=True):
    gv.edge(e1, e2)

gv_path = gv.render(prefix + '.gv')
logging.info('Graph is rendered: %s', gv_path)
