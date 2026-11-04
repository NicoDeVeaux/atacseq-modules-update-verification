#!/usr/bin/env python3
"""Verify selected report evidence custody offline; do not rerun its scientific checks."""
import hashlib
import json
from collections import Counter
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent
PROFILES = {'default', 'controls', 'bowtie2', 'chromap', 'star', 'skip_trimming', 'skip_consensus_peaks'}
ENGINES = {'25.10.4', '26.10.5'}


def load(relative):
    return json.loads((ROOT / relative).read_text())


def check(relative, identity):
    path = PurePosixPath(relative)
    assert not path.is_absolute() and '..' not in path.parts
    full = ROOT / path
    assert full.is_file() and not full.is_symlink() and full.resolve().is_relative_to(ROOT)
    data = full.read_bytes()
    assert len(data) == identity['bytes'] and hashlib.sha256(data).hexdigest() == identity['sha256']
    if 'md5' in identity:
        assert hashlib.md5(data).hexdigest() == identity['md5']
    return data


manifest = load('MANIFEST.json')
expected = {r['path'] for r in manifest['files']}
actual = {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()}
assert actual == expected | {'MANIFEST.json'}
for row in manifest['files']:
    check(row['path'], row)

original = load('ORIGINAL-NATIVE.json')
assert original['run']['conclusion'] == 'failure'
assert len(original['profiles']) == 14
assert {(p['test_case'], p['nextflow_version']) for p in original['profiles']} == {(p, v) for p in PROFILES for v in ENGINES}
assert sum(x['passed'] for x in original['ordinary_tests'].values()) == 16
assert sum(x['failed'] for x in original['ordinary_tests'].values()) == 8
original_by_job = {}
for profile in original['profiles']:
    assert profile['capture_complete'] is False and profile['native_qualification_status'] == 'FAIL'
    prefix = profile['payload_prefix']
    capture = load(prefix + '/capture/manifest.json')
    assert capture['capture_complete'] is False
    assert load(prefix + '/qualification/RESULT.json')['status'] == 'FAIL'
    for row in capture['files']:
        check(prefix + '/capture/' + row['path'], row)
    original_by_job[str(profile['job']['id'])] = (prefix, capture)

summary = load('posthoc/SUMMARY.json')
assert summary['status'] == 'PASS' and len(summary['lanes']) == 14
assert {(l['profile'], l['nextflow']) for l in summary['lanes']} == {(p, v) for p in PROFILES for v in ENGINES}
for lane in summary['lanes']:
    assert lane['qualification_kind'] == 'POSTHOC_REPLAY_NOT_ORIGINAL_NATIVE_PASS'
    assert lane['original_native_capture_status'] == 'PARTIAL' and lane['status'] == 'PASS'
    result = json.loads(check(lane['result'], lane['result_identity']))
    assert result['status'] == 'PASS' and result['qualification_kind'] == lane['qualification_kind']
    check(lane['amended_manifest'], result['capture_manifest'])
    amended = load(lane['amended_manifest'])
    prefix, capture = original_by_job[lane['job_id'].removeprefix('job-')]
    assert amended['files'] == capture['files']
    case = result['cases'][0]
    assert len(result['cases']) == 1 and case['status'] == 'PASS'
    assert [r['order'] for r in case['replays']] == ['forward', 'reverse']
    assert case['replays'][0]['exports'] == case['replays'][1]['exports'] == lane['exports']
    assert case['replays'][0]['semantic']['samples'] == lane['series']
    assert case['replays'][0]['semantic']['numeric_cells'] == lane['numeric_cells']
    for export in lane['exports']:
        records = [r for r in capture['files'] if r['role'] == 'MULTIQC/' + export['name']]
        assert len(records) == 1
        check(prefix + '/capture/' + records[0]['path'], export)
assert all(p['both_engines_exports_byte_identical'] for p in summary['engine_pairs'])

admission = load('admission/SNAPSHOT-ADMISSION.json')
assert {c['profile'] for c in admission['changes']} == {'bowtie2', 'chromap', 'star', 'skip_trimming'}
boundary = load('admission/SOURCE-AND-SNAPSHOT-BOUNDARY.json')
assert boundary['status'] == 'PASS' and boundary['exactly_four_count_MD5_replacements']
assert len(boundary['snapshots']) == 7 and sum(r['changed'] for r in boundary['snapshots']) == 4
assert all(r['unchanged'] for r in boundary['reporting_application_payload_unchanged'])
if (ROOT / 'NATIVE-ATTEMPTS.json').is_file():
    captures = {}
    for attempt in load('NATIVE-ATTEMPTS.json')['attempts']:
        assert attempt['run']['status'] == 'completed'
        assert len(attempt['profiles']) == 14
        assert {(p['test_case'], p['nextflow_version']) for p in attempt['profiles']} == {(p, v) for p in PROFILES for v in ENGINES}
        for profile in attempt['profiles']:
            capture_path = profile['qualification']['path'].removesuffix('qualification/RESULT.json') + 'capture/manifest.json'
            captures[attempt['run']['head_sha'], profile['test_case'], profile['nextflow_version']] = (str(PurePosixPath(capture_path).parent), load(capture_path))
    if (ROOT / 'RAW-ORDER-COMPARISON.json').is_file():
        receipt = load('RAW-ORDER-COMPARISON.json')
        assert hashlib.sha256((ROOT / 'checks/compare_raw_order.original.py').read_bytes()).hexdigest() == receipt['checker_sha256']
        compared = []
        for (source, profile, version), (folder, capture) in sorted(captures.items()):
            if source != receipt['final_source']:
                continue
            old_folder, old_capture = captures[receipt['original_source'], profile, version]
            old = {PurePosixPath(r['path']).name: r for r in old_capture['files'] if r['role'] == 'MULTIQC/staged_raw'}
            new = {PurePosixPath(r['path']).name: r for r in capture['files'] if r['role'] == 'MULTIQC/staged_raw'}
            assert set(old) == set(new)
            for name in sorted(old):
                before = (ROOT / old_folder / old[name]['path']).read_bytes()
                after = (ROOT / folder / new[name]['path']).read_bytes()
                x, y = before.decode().splitlines(), after.decode().splitlines()
                assert x[:2] == y[:2] and Counter(x[2:]) == Counter(y[2:])
                compared.append({'profile': profile, 'nextflow': version, 'name': name,
                    'headers_equal': True, 'complete_rows_multiset_equal': True,
                    'raw_bytes_equal': before == after, 'original_sha256': hashlib.sha256(before).hexdigest(),
                    'final_sha256': hashlib.sha256(after).hexdigest(), 'data_rows': len(x) - 2})
        assert len(compared) == receipt['matrices'] == 80 and compared == receipt['rows']
print(json.dumps({'status': 'PASS', 'files': len(expected), 'original_native_capture': 'PARTIAL',
    'original_native_qualification_passes': 0, 'posthoc_replay_passes': 14,
    'admitted_count_expectations': 4,
    'scope': 'Offline inventory and exact evidence/source/export bindings; no scientific parser rerun or inference about unretained outputs.'}))
