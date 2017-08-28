#!/usr/bin/env python3

import sys, os, operator, math, csv, json, logging, random, re
import argparse
from collections import defaultdict, Counter
from sklearn.metrics import accuracy_score, zero_one_loss
from statistics import mean

parser = argparse.ArgumentParser()
parser.add_argument('n', nargs='?', type=int, default=5000)
args = parser.parse_args()

logging.basicConfig(level=logging.INFO)

BAD_SENSES = {
    'sense1bad': 0,
    'sense2bad': 1,
    'sense3bad': 2,
    'sense4bad': 3,
    'sense5bad': 4,
    'sense6bad': 5
}

BAD_HYPERNYMS = {
    'hypernym1bad': 0,
    'hypernym2bad': 1,
    'hypernym3bad': 2,
    'hypernym4bad': 3
}

def parse(filename, bad, field):
    clusters  = defaultdict(lambda: defaultdict(lambda: list()))
    intruders = {}
    gold      = set()

    for row in open(filename, newline=''):
        row = json.loads(row)

        cid = int(row['data']['cid'])

        for judgement in row['results']['judgments']:
            if judgement['golden']:
                gold.add(cid)

            for vote in judgement['data'][field]:
                clusters[cid][judgement['worker_id']].append((bad[vote], judgement['trust']))

        intruders[cid] = int(row['data']['intruder']) - 1

    return (clusters, intruders, gold)

cluster_answers, cluster_intruders, cluster_gold = parse(
    'job_953322.json', BAD_SENSES,
    'select_the_words_which_are_nonrelevant_for_the_topics_above'
)

hypernym_answers, hypernym_intruders, hypernym_gold = parse(
    'job_952881.json', BAD_HYPERNYMS,
    'select_the_topics_that_are_nonrelevant_for_the_words_above'
)

def answers(filename, data, bad):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)

        writer.writerow(('item', 'rater', 'answer'))

        for cid in cids:
            trusted = {worker_id: trust for worker_id, votes in data[cid].items()
                                        for _, trust in votes}

            trusted = dict(sorted(trusted.items(), key=operator.itemgetter(1)))

            for worker_id, votes in data[cid].items():
                if worker_id not in trusted:
                    continue

                votes = {answer for answer, trust in votes}

                for i in range(len(bad)):
                    writer.writerow(('%d_%d' % (cid, i), worker_id, str(int(i in votes))))

def aggregate(data):
    answers = {}

    for cid in cids:
        c = Counter()

        total = .0

        candidates = [val for sublist in data[cid].values() for val in sublist]

        candidates = sorted(candidates, key=operator.itemgetter(1))[-args.n:]

        for answer, trust in candidates:
            c[answer] += trust
            total     += trust

        answer, trust = c.most_common(1)[0]

        answers[cid] = (answer, trust / total)

    return answers

def badness(data, intruders, scorer=lambda x: x):
    values = {}

    for cid in cids:
        c = Counter()

        total = .0

        candidates = [val for sublist in data[cid].values() for val in sublist]

        candidates = sorted(candidates, key=operator.itemgetter(1))[-args.n:]

        for answer, trust in candidates:
            if answer != intruders[cid]:
                answer = None

            c[answer] += scorer(trust)
            total     += scorer(trust)

        values[cid] = c[None] / float(total)

    return values

def scores(true, pred):
    return (accuracy_score(true, pred), zero_one_loss(true, pred))

# cluster-based accuracy

cids          = sorted(list(cluster_answers.keys() - cluster_gold))

cluster_agg   = aggregate(cluster_answers)
cluster_true  = [cluster_intruders[cid] for cid in cids]
cluster_pred  = [cluster_agg[cid][0]    for cid in cids]
cluster_bad   = badness(cluster_answers, cluster_intruders, lambda x: 1)

print('Clusters (%d non-golden out of %d):\taccuracy=%.3f, zero_one_loss=%.3f, avg_badness=%.3f.' % (
    len(cids), len(cluster_answers), *scores(cluster_true,  cluster_pred), mean(cluster_bad.values()))
)

answers('clusters-votes.csv', cluster_answers, BAD_SENSES)

# hypernym-based accuracy

cids           = sorted(list(hypernym_answers.keys() - hypernym_gold))

hypernym_agg   = aggregate(hypernym_answers)
hypernym_true  = [hypernym_intruders[cid] for cid in cids]
hypernym_pred  = [hypernym_agg[cid][0]   for cid in cids]
hypernym_bad   = badness(hypernym_answers, hypernym_intruders, lambda x: 1)

print('Hypernyms (%d non-golden out of %d):\taccuracy=%.3f, zero_one_loss=%.3f, avg_badness=%.3f.' % (
    len(cids), len(hypernym_answers), *scores(hypernym_true,  hypernym_pred), mean(hypernym_bad.values()))
)

answers('hypernyms-votes.csv', hypernym_answers, BAD_HYPERNYMS)

# results

def hmean(a, b):
    if a is None or b is None:
        return None

    ab = a + b

    if ab == 0:
        return 0.

    return 2 * a * b / ab

with open('results.tsv', 'w', newline='') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(('cid', 'badness', 'cintruder', 'canswer', 'cconfidence', 'cbadness', 'hintruder', 'hanswer', 'hconfidence', 'hbadness'))

    for cid in cids:
        _cbadness = cluster_bad.get(cid,  None)
        _hbadness = hypernym_bad.get(cid, None)
        _badness  = hmean(_cbadness, _hbadness)

        _cintruder   = cluster_intruders.get(cid, None)
        _canswer     = cluster_agg.get(cid, [None, None])[0]
        _cconfidence = cluster_agg.get(cid, [None, None])[1]

        _hintruder   = hypernym_intruders.get(cid, None)
        _hanswer     = hypernym_agg.get(cid, [None, None])[0]
        _hconfidence = hypernym_agg.get(cid, [None, None])[1]

        writer.writerow((cid, _badness, _cintruder, _canswer, _cconfidence, _cbadness, _hintruder, _hanswer, _hconfidence, _hbadness))

# import IPython; IPython.embed()
