#!/usr/bin/env python3
"""Check the compact ledger inventory and identity/status contracts offline."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent
manifest = json.loads((ROOT/'MANIFEST.json').read_text())
actual = {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()}
expected = {x['path'] for x in manifest['files']}
assert actual == expected | {'MANIFEST.json'}
for row in manifest['files']:
    p = ROOT/row['path']
    assert not p.is_symlink() and p.resolve().is_relative_to(ROOT)
    b = p.read_bytes()
    assert len(b) == row['bytes'] and hashlib.sha256(b).hexdigest() == row['sha256']
runs = json.loads((ROOT/'RUNS.json').read_text())
ids = [x['campaign_id'] for x in runs['campaigns']]
assert len(ids) == len(set(ids)) == 9
for campaign in runs['campaigns']:
    for assertion in campaign['scientific_assertions']:
        assert assertion['status'] in ('PASS','FAIL','UNKNOWN','NOT_RUN')
    for run in campaign['runs']:
        for key in ('execution','nf_test','native_CI'):
            assert run[key]['status'] in ('PASS','FAIL','UNKNOWN','NOT_RUN')
integration = json.loads((ROOT/'receipts/native-fingerprint-integration.json').read_text())
assert hashlib.sha256(json.dumps(runs['campaigns'][:8], sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest() == integration['preserved_campaigns_canonical_sha256']
assert ids[-1] == 'fingerprint-native-ci-20261104'
hashes = json.loads((ROOT/'HASH-INDEX.json').read_text())['hashes']
assert all(re.fullmatch(r'[0-9a-f]{32}|[0-9a-f]{40}|[0-9a-f]{64}', h) for h in hashes)
ci = json.loads((ROOT/'receipts/pr476-final-native-ci.json').read_text())
assert ci['PASS'] and ci['raw_underlying_tests_all_pass']
assert ci['cases_per_engine'] == {'25.10.4':12,'26.10.5':12}
assert all(sum(len(x['tests']) for x in ci['cases'] if x['version']==v)==12 for v in ['25.10.4','26.10.5'])
maps = json.loads((ROOT/'SOURCE-MAPS.json').read_text())
assert maps['fingerprint-literal25']['file_sha256']['bin/multiqc_fingerprint.py'].startswith('723bf5')
assert maps['fingerprint-literal26']['file_sha256']['bin/multiqc_fingerprint.py'].startswith('532bfb')
print(json.dumps({'status':'PASS','files':len(expected),'campaigns':len(ids),'indexed_digests':len(hashes),
                  'scope':'Ledger integrity and status/source contracts; no scientific rerun or public-byte coverage inference.'}))
