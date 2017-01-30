#!/usr/bin/env python

from __future__ import print_function
import logging, sys

reload(sys)
sys.setdefaultencoding('utf8')

logging.basicConfig(level=logging.INFO)

import params

try:
    import cPickle as pickle
except:
    import pickle

import lmdb

DATABASE = '/home/dmitry/lmdb'

env = lmdb.open(DATABASE, create=False, readonly=True, max_dbs=10, map_size=1024 * 1024 * 1024 * 20)
senses_db, egos_db = env.open_db('senses'), env.open_db('egos')

with env.begin() as txn:
    with txn.cursor(db=egos_db) as curs:
        for sense, ego in curs:
            cws = pickle.loads(ego)
            print(cws)

            denominator = float(len(reduce(set.union, cws.values())))
            matched = next((k for k, v in cws.items() if len(v) / denominator >= params.P and sense in v), None)

            if matched is None:
                logging.warn('Skipped by clustering: %s', sense)
                continue

            nodes, edges = cws[matched], set()

            for node1 in nodes:
                value = txn.get(node1, db=senses_db)
                if not value:
                    continue
                senses = pickle.loads(value)
                adjacent = [n for n in senses if n in nodes and n != node1]
                for node2 in adjacent:
                    print('{:s}\t{:s}'.format(*sorted([node1, node2])))
