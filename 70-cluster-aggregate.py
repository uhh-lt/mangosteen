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
    'sense1bad': 0,
    'sense2bad': 1,
    'sense3bad': 2,
    'sense4bad': 3,
    'sense5bad': 4,
    'sense6bad': 5
}

clusters  = defaultdict(lambda: list())
intruders = {}

for row in open(os.path.join(prefix, '61-cluster-votes.json')):
    row = json.loads(row)
    cid = row['data']['cid']
    # nice attempt, American English, but no.
    # for vote in row['results']['judgments'][0]['data']['select_the_words_which_are_nonrelevant_for_the_topics_above']:
    for judgement in row['results']['judgments']:
        for vote in judgement['data']['select_the_words_which_are_nonrelevant_for_the_topics_above']:
            clusters[cid].append(BAD[vote])
    intruders[cid] = int(row['data']['intruder']) - 1

with open(os.path.join(prefix, '70-cluster-aggregated.tsv'), 'wb') as f:
    writer = csv.writer(f, dialect='excel-tab', lineterminator='\n')
    writer.writerow(('cid', 'intruder', 'votes', 'intruder-bad', 'sense-bad', 'cbadness', 'cbad'))
    for cid, votes in clusters.items():
        intruder_bad = len([v for v in votes if v == intruders[cid]])
        sense_bad    = len([v for v in votes if v != intruders[cid]])
        counter      = Counter([v for v in clusters[cid] if not v == intruders[cid]]).most_common(1)
        cluster_bad  = 1 if len(counter) > 0 and counter[0][1] >= 2 else 0
        writer.writerow((cid, intruders[cid], len(votes), intruder_bad, sense_bad, sense_bad / float(len(votes)), cluster_bad))
