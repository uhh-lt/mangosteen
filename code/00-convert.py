#!/usr/bin/env python

from __future__ import print_function
import logging, sys, csv, re, operator, os
from collections import OrderedDict

reload(sys)
sys.setdefaultencoding('utf8')

logging.basicConfig(level=logging.INFO)

try:
    import cPickle as pickle
except:
    import pickle

import lmdb

DATABASE = os.path.join(os.getcwd(), 'lmdb')

N = 20

env = lmdb.open(DATABASE, max_dbs=10, map_size=1024 * 1024 * 1024 * 20)
senses_db, isas_db = env.open_db('senses'), env.open_db('isas')

with open('ddt.tsv') as f:
    reader = csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
    with env.begin(db=senses_db, write=True) as txn:
        for row in reader:
            sense = '#'.join((row['word'], row['cid']))

            if row['cluster']:
                senses = [kv.split(':', 2) for kv in row['cluster'].split(',')]
                senses = {sense[0]: float(sense[1]) for sense in senses if len(sense) == 2}
                senses = dict(OrderedDict(sorted(senses.items(), key=operator.itemgetter(1), reverse=True)[:N]))
                txn.put(sense, pickle.dumps(senses))
    logging.info('Finished the senses database')

    f.seek(0)
    with env.begin(db=isas_db, write=True) as txn:
        for row in reader:
            sense = '#'.join((row['word'], row['cid']))

            if row['isas']:
                isas = [kv.split(':', 2) for kv in row['isas'].split(',')]
                isas = {sense[0]: float(sense[1]) for sense in isas if len(sense) == 2}
                txn.put(sense, pickle.dumps(isas))
    logging.info('Finished the isas database')
