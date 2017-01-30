#!/usr/bin/env python

from __future__ import print_function
from collections import OrderedDict
import sys, os, math, csv

reload(sys)
sys.setdefaultencoding('utf8')
csv.field_size_limit(sys.maxsize)

try:
    import cPickle as pickle
except:
    import pickle

freqs = {}

with open('freq-59g-mwe62m.csv') as f:
    reader = csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in reader:
        freqs[row['word']] = math.log(float(row['freq']))

try:
    os.remove('60-frequencies.pickle')
except OSError:
    pass

with open('60-frequencies.pickle', 'wb') as f:
    pickle.dump(freqs, f, pickle.HIGHEST_PROTOCOL)


