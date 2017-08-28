#!/usr/bin/env python

import argparse
import pandas as pd
from sklearn.metrics import accuracy_score, roc_auc_score, precision_score, recall_score, f1_score

parser = argparse.ArgumentParser()
parser.add_argument('n', nargs='?', type=int, default=5)
args = parser.parse_args()

df = pd.read_csv('hyper-clusters-patterns.csv', delimiter='\t')
df.drop_duplicates(subset=['sense', 'hypernym', 'source'], inplace=True)

# df = df[df['hypernym'] != '?']
patterns = df[df['source'] == 'patterns']
clusters = df[df['source'] == 'clusters']

joint = pd.merge(patterns, clusters, on=('sense', 'hypernym'))

def load(path):
    results = pd.read_csv(path)
    results = results[~results['_golden']]
    results['relevant'] = results['your_opinion'] == 'yes'
    results['confidence'] = results['_trust']
    results['worker'] = results['_worker_id']
    results = results[['sense', 'hypernym', 'source', 'relevant', 'confidence', 'worker']]
    return results

results1 = load('f971991.csv')
results2 = load('f981161.csv')
results3 = load('f984024.csv')

results = results1.append(results2).append(results3)
results.drop_duplicates(subset=['sense', 'hypernym', 'worker'], inplace=True)

results['vote'] = results.apply(lambda r: r['confidence'] if r['relevant'] else -r['confidence'], axis=1)
results = results.groupby(['sense', 'hypernym']).apply(lambda r: r.sort_values(by='confidence', ascending=False).head(args.n))

votes = results.groupby(['sense', 'hypernym']).agg({'vote': sum})
votes.reset_index(inplace=True)
votes['key'] = list(zip(votes['sense'], votes['hypernym']))

gold = list(zip(votes['key'], votes['vote'] > 0))
true = [int(value) for pair, value in gold]

patterns_pairs = set(zip(patterns['sense'], patterns['hypernym']))
patterns_pred  = [int(pair in patterns_pairs) for pair, _ in gold]

clusters_pairs = set(zip(clusters['sense'], clusters['hypernym']))
clusters_pred  = [int(pair in clusters_pairs) for pair, _ in gold]

def scores(true, pred):
    return (accuracy_score(true, pred), roc_auc_score(true, pred), precision_score(true, pred), recall_score(true, pred), f1_score(true, pred))

print('%d pairs annotated including %d by patterns and %d by clusters; %d votes total.' % (len(gold), sum(patterns_pred), sum(clusters_pred), len(results)))
print('Patterns have accuracy=%.3f, roc_auc=%.3f, precision=%.3f, recall=%.3f, f1_score=%.3f.' % scores(true, patterns_pred))
print('Clusters have accuracy=%.3f, roc_auc=%.3f, precision=%.3f, recall=%.3f, f1_score=%.3f.' % scores(true, clusters_pred))

units = {pair: i for i, (pair, _) in enumerate(gold)}

results['unit'] = results.apply(lambda r: units[(r['sense'], r['hypernym'])], axis=1)
results.to_csv('cf-results.csv', index=False)

# import IPython; IPython.embed()
