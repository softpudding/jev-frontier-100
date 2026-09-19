"""Auditable scoring and stratified paired-template bootstrap; no LLM judge."""
import argparse
import collections
import csv
import json
import math
from pathlib import Path
import random
import statistics
from .core import ROOT,load_items,presented
from .runner import model_slug


def quantile(xs,p):
    ordered=sorted(xs)
    ix=(len(ordered)-1)*p;lo=math.floor(ix);hi=math.ceil(ix)
    return ordered[lo]+(ordered[hi]-ordered[lo])*(ix-lo)


def bootstrap_pair_means(pair_values,pair_domains,draws=5000):
    groups=collections.defaultdict(list)
    for pair,value in pair_values.items():groups[pair_domains[pair]].append(value)
    rng=random.Random(92026);samples=[]
    for _ in range(draws):
        values=[]
        for domain in sorted(groups):
            group=groups[domain]
            values.extend(rng.choices(group,k=len(group)))
        samples.append(statistics.mean(values))
    return [quantile(samples,.025),quantile(samples,.975)]


def summarize(rows,items,trials,draws=5000):
    byid={i['id']:i for i in items};seen=set()
    for r in rows:
        key=(r['item_id'],r['trial'])
        if key in seen:raise ValueError(f'Duplicate scored checkpoint: {key}')
        seen.add(key)
        if r['item_id'] not in byid or not 0<=r['trial']<trials:raise ValueError('Unknown item/trial')
        _,gold=presented(byid[r['item_id']],r['trial'])
        if r['gold']!=gold:raise ValueError('Logged gold differs from frozen dataset')
        if r['correct']!=(r['status']=='ok' and r['answer']==gold):raise ValueError('Scoring inconsistency')
    complete=len(seen)==len(items)*trials
    statuses=collections.Counter(r['status'] for r in rows)
    valid=[r for r in rows if r['status']=='ok']
    groups={}
    for field in ['domain','difficulty']:
        groups[field]={}
        for name in sorted({i[field] for i in items}):
            subset=[r for r in rows if byid[r['item_id']][field]==name]
            groups[field][name]={'correct':sum(r['correct'] for r in subset),'n':len(subset),'expected_n':sum(i[field]==name for i in items)*trials,
                                 'accuracy':statistics.mean(r['correct'] for r in subset) if subset else None}
    item_scores=collections.defaultdict(list);pair_trials=collections.defaultdict(list)
    for r in rows:
        item_scores[r['item_id']].append(int(r['correct']))
        pair_trials[(byid[r['item_id']]['pair_id'],r['trial'])].append(int(r['correct']))
    per_pair=collections.defaultdict(list)
    for id,values in item_scores.items():per_pair[byid[id]['pair_id']].append(statistics.mean(values))
    pair_values={p:statistics.mean(v) for p,v in per_pair.items()}
    pair_domains={i['pair_id']:i['domain'] for i in items}
    consistent=0;fully_observed=0
    for item in items:
        rs=[r for r in rows if r['item_id']==item['id']]
        if len(rs)==trials and all(r['status']=='ok' for r in rs):
            meanings=[presented(item,r['trial'])[0]['options'][r['answer']] for r in rs]
            fully_observed+=1;consistent+=len(set(meanings))==1
    return {'complete':complete,'records':len(rows),'expected_records':len(items)*trials,
            'correct':sum(r['correct'] for r in rows),'accuracy':statistics.mean(r['correct'] for r in rows) if rows else None,
            'accuracy_95ci':bootstrap_pair_means(pair_values,pair_domains,draws) if complete else None,
            'status_counts':dict(statuses),'valid_completion_rate':len(valid)/len(rows) if rows else None,
            'accuracy_among_valid':statistics.mean(r['correct'] for r in valid) if valid else None,
            'pair_joint_accuracy':statistics.mean(all(v) for v in pair_trials.values() if len(v)==2) if any(len(v)==2 for v in pair_trials.values()) else None,
            'semantic_consistency':consistent/fully_observed if fully_observed else None,
            'consistency_eligible_items':fully_observed,
            'latency_median_ms':statistics.median(r['elapsed_ms'] for r in rows) if rows else None,
            'groups':groups,'pair_values':pair_values,'pair_domains':pair_domains}

