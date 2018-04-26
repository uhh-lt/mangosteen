#!/usr/bin/env python

from __future__ import print_function
import sys, csv, operator, logging, os
from collections import Counter, OrderedDict, defaultdict
from math import log
from sklearn.feature_extraction import DictVectorizer
from scipy.spatial.distance import cosine

reload(sys)
sys.setdefaultencoding('utf8')

logging.basicConfig(level=logging.INFO)

import params

try:
    import cPickle as pickle
except:
    import pickle

import lmdb

DATABASE = os.path.join(os.getcwd(), 'lmdb')

env = lmdb.open(DATABASE, max_dbs=10, map_size=1024 * 1024 * 1024 * 20)
isas_db, hypernyms_db = env.open_db('isas'), env.open_db('hypernyms')

logging.info('Operating in "%s" mode', params.H)

idf = defaultdict(lambda: 0)
ambiguity = defaultdict(lambda: defaultdict(dict))

with env.begin(db=isas_db) as txn:
    D = float(txn.stat()['entries'])
    with txn.cursor() as curs:
        for sense, value in curs:
            for hypernym, sim in pickle.loads(value).items():
                word = hypernym.rsplit('#', 1)[0]
                ambiguity[word][hypernym][sense] = sim
                idf[word] += 1
    for k, v in idf.items():
        idf[k] = log(D / v)

with open('26-cw.txt') as fr, open('30-hypernyms.txt', 'w') as fw:
    reader = csv.reader(fr, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in reader:
        cid = row[0]
        cluster = {sense: 1 for sense in row[2].split(', ') if sense}
        isas, hypernyms = {}, None

        with env.begin(db=isas_db) as txn:
            for sense in cluster:
                value = txn.get(sense)
                if value:
                    isas[sense] = {k.rsplit('#', 1)[0]: v for k, v in pickle.loads(value).items()}

        if params.H == 'tf':
            counters = [Counter(isas[r]) for r in cluster if r in isas]
            if counters:
                hypernyms = OrderedDict(reduce(operator.add, counters).most_common(5))
        elif params.H == 'tfidf':
            counters = [Counter({k: idf[k] for k in isas[r]}) for r in cluster if r in isas]
            if counters:
                hypernyms = OrderedDict(reduce(operator.add, counters).most_common(5))
        else:
            raise NotImplemented

        if hypernyms:
            for hypernym in hypernyms.copy():
                similarities = {}
                for h_sense, senses in ambiguity[hypernym].items():
                    v = DictVectorizer(sparse=False)
                    D = [cluster, senses]
                    similarities[h_sense] = 1 - cosine(*v.fit_transform(D))
                h_sense = max(similarities.items(), key=operator.itemgetter(1))[0]
                hypernyms[h_sense] = hypernyms[hypernym]
                hypernyms.pop(hypernym)

            with env.begin(db=hypernyms_db, write=True) as txn:
                txn.put(cid, pickle.dumps(hypernyms))
            print('{:s}\t{:s}'.format(cid, ','.join('{:s}:{:f}'.format(*h) for h in hypernyms.items())), file=fw)
