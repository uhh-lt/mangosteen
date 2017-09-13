#!/usr/bin/env python

from __future__ import print_function
import sys, csv, logging
import pattern.en

reload(sys)
sys.setdefaultencoding('utf8')

logging.basicConfig(level=logging.INFO)

import params

logging.info('POS filtering enabled: %s', str(params.N == 1))

POS = {'NOUN', 'MWE'}
NOUNS = {n.lower() for n, p in pattern.en.lexicon.items() if pattern.en.NOUN in p}

def pos(word):
    if word.lower() in NOUNS:
        return 'NOUN'
    if ' ' in word:
        return 'MWE'
    if word in pattern.en.lexicon:
        return pattern.en.lexicon[word]
    else:
        return ''

cache = {}

with open('24-prune.txt') as fr, open('25-pos.txt', 'w') as fw:
    reader = csv.reader(fr, delimiter='\t', quoting=csv.QUOTE_NONE)
    if params.N == 1:
        for row in reader:
            sense1, sense2 = row[0].rsplit('#', 1), row[1].rsplit('#', 1)
            cache.setdefault(sense1[0], pos(sense1[0]))
            cache.setdefault(sense2[0], pos(sense2[0]))
            pos1, pos2 = cache[sense1[0]], cache[sense2[0]]
            if pos1 in POS and pos2 in POS:
                print('{:s}\t{:s}\t{:s}'.format(row[0], row[1], row[2]), file=fw)
                # node1 = '{:s}_{:s}#{:s}'.format(sense1[0], pos1, sense1[1])
                # node2 = '{:s}_{:s}#{:s}'.format(sense2[0], pos2, sense2[1])
                # print('{:s}\t{:s}\t{:s}'.format(node1, node2, row[2]), file=fw)
    else:
        for row in reader:
            print('{:s}\t{:s}\t{:s}'.format(row[0], row[1], row[2]), file=fw)
