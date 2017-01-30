#!/usr/bin/env python

from __future__ import print_function
import sys, os, operator, math, csv, json, logging, random, re
from collections import defaultdict, Counter

reload(sys)
sys.setdefaultencoding('utf8')
csv.field_size_limit(sys.maxsize)

prefix = sys.argv[1] if len(sys.argv) > 1 else ''

logging.basicConfig(level=logging.INFO)

BAD = {
    'hypernym1bad': 0,
    'hypernym2bad': 1,
    'hypernym3bad': 2,
    'hypernym4bad': 3
}

clusters  = defaultdict(lambda: list())
intruders = {}

for row in open(os.path.join(prefix, '62-hypernym-votes.json')):
    row = json.loads(row)
    cid = row['data']['cid']
    # nice attempt, American English, but no.
    # for vote in row['results']['judgments'][0]['data']['select_the_topics_that_are_nonrelevant_for_the_words_above']:
    for judgement in row['results']['judgments']:
        for vote in judgement['data']['select_the_topics_that_are_nonrelevant_for_the_words_above']:
            clusters[cid].append(BAD[vote])
    intruders[cid] = int(row['data']['intruder']) - 1

with open(os.path.join(prefix, '71-hypernym-aggregated.tsv'), 'wb') as f:
    writer = csv.writer(f, dialect='excel-tab', lineterminator='\n')
    writer.writerow(('cid', 'intruder', 'votes', 'intruder-bad', 'hypernym-bad', 'hbadness', 'hbad'))
    for cid, votes in clusters.items():
        intruder_bad = len([v for v in votes if v == intruders[cid]])
        hypernym_bad = len([v for v in votes if v != intruders[cid]])
        counter      = Counter([v for v in clusters[cid] if not v == intruders[cid]]).most_common(1)
        cluster_bad  = 1 if len(counter) > 0 and counter[0][1] >= 2 else 0
        writer.writerow((cid, intruders[cid], len(votes), intruder_bad, hypernym_bad, hypernym_bad / float(len(votes)), cluster_bad))
