#!/usr/bin/env python3
"""Find a complete digest/prefix or a result in the compact run ledger."""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('query', nargs='?')
parser.add_argument('--result', help='Find campaigns containing this result/text, such as 299580')
parser.add_argument('--limit', type=int, default=20)
parser.add_argument('--json', action='store_true', help='Emit full machine-readable hashes and evidence')
args = parser.parse_args()

def show_campaigns(campaigns):
    for campaign in campaigns:
        print(f"\n{campaign['campaign_id']}: {campaign['title']}")
        for run in campaign.get('runs', []):
            identities = [f'{key}={value[:6]}' for key,value in run.get('literal_execution_source', {}).items()
                          if isinstance(value,str) and re.fullmatch('[0-9a-f]{32,64}',value)]
            statuses = [f"{key}={run.get(key,{}).get('status','UNKNOWN')}"
                        for key in ['execution','nf_test','native_CI']]
            print(f"  {run['run_id']}: " + '; '.join(identities + statuses))
        for assertion in campaign.get('scientific_assertions', []):
            print(f"  {assertion['status']}: {assertion['statement']}")

if args.result is not None:
    data = json.loads((ROOT/'RUNS.json').read_text())
    selected = [x for x in data['campaigns'] if args.result.lower() in json.dumps(x).lower()]
    if args.json:
        print(json.dumps(selected[:args.limit], indent=2))
    else:
        print(f'{len(selected)} matching campaigns')
        show_campaigns(selected[:args.limit])
elif args.query:
    hashes = json.loads((ROOT/'HASH-INDEX.json').read_text())['hashes']
    matches = {k:v for k,v in hashes.items() if k.startswith(args.query.lower())}
    selected=dict(list(matches.items())[:args.limit])
    ids={cid for rows in selected.values() for row in rows for cid in row.get('campaign_ids',[])}
    campaigns=json.loads((ROOT/'RUNS.json').read_text())['campaigns']
    related=[{'campaign_id':x['campaign_id'],'title':x['title'],'runs':x['runs'],'scientific_assertions':x['scientific_assertions']} for x in campaigns if x['campaign_id'] in ids]
    if args.json:
        print(json.dumps({'matching_digests':len(matches), 'matches':selected,'related_campaigns':related}, indent=2))
    else:
        print(f'{len(matches)} matching digests')
        for digest,refs in selected.items():
            print(f'{digest[:6]}: {len(refs)} evidence references')
        show_campaigns(related)
else:
    parser.error('Supply a digest/prefix or --result text')
