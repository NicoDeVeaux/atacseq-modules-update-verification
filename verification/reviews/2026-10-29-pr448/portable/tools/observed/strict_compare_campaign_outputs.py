#!/usr/bin/env python3
"""Compare collected campaign artifacts offline; completeness is not scientific PASS."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re

REFERENCE = Path(__file__).resolve().parents[2] / 'atacseq-modules-update-verification-evidence/verification/scripts/compare_featurecounts.py'
REFERENCE_SHA = '211c6b2f871fc5c2d9aa6c9a4f9b0a2c25fe2273a7dedb7ad9da2d689a6bdf93'
LIBRARY_KINDS = {'flagstat', 'stats', 'idxstats', 'scale', 'markduplicates'}
REQUIRED = LIBRARY_KINDS | {'counts', 'bed', 'versions'}


def reference(path=REFERENCE):
    if hashlib.sha256(path.read_bytes()).hexdigest() != REFERENCE_SHA:
        raise ValueError('Verified featureCounts comparator source changed or is unavailable')
    spec = importlib.util.spec_from_file_location('verified_featurecounts', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load(path, default=None):
    return json.loads(path.read_text()) if path.exists() else default


def scalar(value):
    try:
        number = float(value)
        return int(value) if re.fullmatch(r'[+-]?\d+', value) else number if math.isfinite(number) else value
    except ValueError:
        return value


def category(path):
    name = path.name.lower()
    if re.search(r'featurecounts\.(tsv|txt)$', name): return 'counts'
    if 'consensus_peaks' in name and name.endswith('.bed'): return 'bed'
    if name.endswith('.flagstat'): return 'flagstat'
    if name.endswith('.idxstats'): return 'idxstats'
    if name.endswith('.stats'): return 'stats'
    if name.endswith('scale_factor.txt'): return 'scale'
    if ('markduplicates' in name or '.mkd.sorted.' in name) and name.endswith('.metrics.txt'): return 'markduplicates'
    if '/picard_metrics/' in '/' + path.as_posix() and (name.endswith('_metrics') or name.endswith('.metrics.txt')): return 'picard'
    if 'software' in name and 'versions' in name and path.suffix in ('.yml', '.yaml'): return 'versions'


def canonical(path):
    return path.as_posix().replace('.featureCounts.txt', '.featureCounts.tsv')


def count_table(path, ref):
    data = [line.rstrip('\n').split('\t') for line in path.read_text().splitlines() if line and not line.startswith('#')]
    if not data or data[0][:6] != ['Geneid', 'Chr', 'Start', 'End', 'Strand', 'Length']:
        raise ValueError('Invalid featureCounts header')
    def sample(value):
        value = ref.normalize_sample(value.replace('\\', '/').rsplit('/', 1)[-1])
        return re.sub(r'\.m(?:Lb|Rp)\..*$', '', value)
    names = [sample(value) for value in data[0][6:]]
    if not names or len(names) != len(set(names)):
        raise ValueError('Missing or ambiguous normalized sample columns')
    seen, metadata = set(), {}
    for fields in data[1:]:
        if len(fields) != len(data[0]): raise ValueError('Truncated or extra featureCounts columns')
        key = (fields[1], fields[2], fields[3])
        if key in seen: raise ValueError('Duplicate coordinate key')
        if int(fields[2]) < 1 or int(fields[3]) < int(fields[2]): raise ValueError('Invalid count coordinates')
        if any(int(value) < 0 for value in fields[6:]): raise ValueError('Negative counts')
        seen.add(key)
        metadata[':'.join(key)] = fields[4:6]
    version, original, rows = ref.parse_featurecounts(path)
    rename = dict(zip(original, names))
    return version, names, {key: {rename[name]: value for name, value in values.items()} for key, values in rows.items()}, metadata


def compare_counts(left, right, ref):
    a, b = count_table(left, ref), count_table(right, ref)
    result = ref.compare(('unfixed', *a[:3]), ('fixed', *b[:3]))
    result['changed_cells'] = [{'coordinate': key, 'sample': sample, 'unfixed': a[2][key][sample], 'fixed': b[2][key][sample]}
        for key in sorted(a[2].keys() & b[2].keys()) for sample in sorted(set(a[1]) & set(b[1]))
        if a[2][key][sample] != b[2][key][sample]]
    for label, own, other in [('unfixed', a, b), ('fixed', b, a)]:
        result['only_' + label + '_rows'] = [{'coordinate': key, 'counts': own[2][key]} for key in sorted(own[2].keys() - other[2].keys())]
        result['only_' + label + '_sample_counts'] = {sample: [{'coordinate': key, 'count': own[2][key][sample]} for key in sorted(own[2])]
            for sample in own[1] if sample not in other[1]}
    result['annotation_differences'] = differences(a[3], b[3])
    result['equal_counts_and_coordinates'] = (set(a[1]) == set(b[1]) and set(a[2]) == set(b[2]) and not result['changed_cells'])
    return result


def bed(path):
    rows = []
    for line in path.read_text().splitlines():
        if not line or line.startswith(('#', 'track', 'browser')): continue
        values = line.split()
        start, end = int(values[1]), int(values[2])
        if start < 0 or end <= start: raise ValueError('Invalid BED interval')
        rows.append((values[0], start, end))
    return set(rows), len(rows)


def merged(intervals):
    result = []
    for chrom, start, end in sorted(intervals):
        if result and result[-1][0] == chrom and start <= result[-1][2]:
            result[-1] = (chrom, result[-1][1], max(end, result[-1][2]))
        else: result.append((chrom, start, end))
    return result


def compare_bed(left, right):
    a, na = bed(left); b, nb = bed(right)
    ma, mb, intersection, i, j = merged(a), merged(b), 0, 0, 0
    while i < len(ma) and j < len(mb):
        ca, sa, ea = ma[i]; cb, sb, eb = mb[j]
        if ca < cb: i += 1; continue
        if cb < ca: j += 1; continue
        intersection += max(0, min(ea, eb) - max(sa, sb))
        if ea <= eb: i += 1
        else: j += 1
    union_bp = sum(e - s for _, s, e in ma + mb) - intersection
    return {'unfixed_intervals': len(a), 'fixed_intervals': len(b), 'shared_exact_intervals': len(a & b),
        'only_unfixed': sorted(a - b), 'only_fixed': sorted(b - a),
        'duplicate_intervals': {'unfixed': na - len(a), 'fixed': nb - len(b)},
        'exact_interval_jaccard': len(a & b) / len(a | b) if a | b else None,
        'intersection_bp': intersection, 'union_bp': union_bp,
        'basepair_jaccard': intersection / union_bp if union_bp else None}


def parsed(path, kind):
    lines = path.read_text().splitlines()
    if kind == 'scale':
        value = float(path.read_text().strip())
        if not math.isfinite(value): raise ValueError('Non-finite scale factor')
        return value
    if kind == 'versions':
        result = {}
        for line in lines:
            match = re.fullmatch(r'\s+([^:]+):\s*(\S.*?)\s*', line)
            if match: result.setdefault(match[1], set()).add(match[2].strip('\'"'))
        if not result: raise ValueError('No software version entries')
        return {key: sorted(values) for key, values in result.items()}
    if kind == 'flagstat':
        result = {}
        for line in lines:
            match = re.match(r'^(\d+)\s+\+\s+(\d+)\s+(.+)$', line)
            if match:
                key = re.sub(r'\s+\((?:QC-passed reads.*|[^)]*%[^)]*|N/A[^)]*)\)$', '', match[3]).strip()
                if key in result: raise ValueError('Duplicate flagstat label')
                result[key] = [int(match[1]), int(match[2])]
        if 'in total' not in result: raise ValueError('Missing flagstat totals')
        def rate(n, d): return result[n][0] / result[d][0] if n in result and d in result and result[d][0] else None
        return {'counts_qc_pass_fail': result, 'qc_pass_rates': {'mapped_over_total': rate('mapped', 'in total'),
            'primary_mapped_over_primary': rate('primary mapped', 'primary'), 'duplicates_over_total': rate('duplicates', 'in total')}}
    if kind == 'idxstats':
        result = {}
        for line in lines:
            fields = line.split('\t')
            if len(fields) != 4 or fields[0] in result: raise ValueError('Invalid/duplicate idxstats row')
            result[fields[0]] = [int(value) for value in fields[1:]]
            if any(value < 0 for value in result[fields[0]]): raise ValueError('Negative idxstats value')
        if not result: raise ValueError('Empty idxstats')
        return {'contigs_length_mapped_unmapped': result, 'mapped': sum(v[1] for v in result.values()), 'unmapped': sum(v[2] for v in result.values())}
    if kind == 'stats':
        records = [line.split('\t') for line in lines if line and not line.startswith('#')]
        if not any(row[0] == 'SN' for row in records): raise ValueError('Missing samtools stats SN records')
        return sorted([[scalar(value) for value in row] for row in records], key=lambda value: json.dumps(value))
    sections, header = [], None
    for line in lines:
        if not line.strip(): header = None; continue
        if line.startswith('#'): continue
        fields = line.split('\t')
        if header is None:
            header = fields; sections.append({'header': header, 'rows': []})
        else:
            if len(fields) != len(header): raise ValueError('Picard metrics column mismatch')
            sections[-1]['rows'].append([scalar(value) for value in fields])
    if not sections: raise ValueError('No Picard metrics tables')
    if not all(section['rows'] for section in sections): raise ValueError('Empty Picard metrics table')
    for section in sections: section['rows'].sort(key=json.dumps)
    return sections


def differences(a, b, key=''):
    if isinstance(a, dict) and isinstance(b, dict):
        return [difference for child in sorted(a.keys() | b.keys()) for difference in differences(a.get(child, {'missing': True}), b.get(child, {'missing': True}), key + '/' + str(child))]
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        return [difference for index, (x, y) in enumerate(zip(a, b)) for difference in differences(x, y, key + '/' + str(index))]
    return [] if a == b else [{'key': key, 'unfixed': a, 'fixed': b}]


def files_for(root, run, manifest):
    directory = root / 'outputs' / run['name']
    files, issues = {}, []
    records = manifest.get('files') or []
    for record in records:
        if isinstance(record, str): record = {'relative_path': record}
        rel = record.get('relative_path') or record.get('path') or ''
        path = Path(rel)
        if not rel or path.is_absolute() or '..' in path.parts:
            issues.append('Unsafe manifest relative path'); continue
        local = directory / path
        if not local.resolve().is_relative_to(directory.resolve()) or record.get('status', 'downloaded') not in ('downloaded', 'collected', 'ok') or not local.is_file() or local.is_symlink():
            issues.append('Unavailable artifact: ' + rel); continue
        if record.get('sha256') and hashlib.sha256(local.read_bytes()).hexdigest() != record['sha256']:
            issues.append('Hash mismatch: ' + rel); continue
        if record.get('source_workflow_id') and record['source_workflow_id'] != manifest.get('workflow_id'):
            issues.append('Artifact belongs to another workflow ID: ' + rel); continue
        key = canonical(path)
        if key in files: issues.append('Ambiguous artifact path: ' + key)
        else: files[key] = local
    return files, issues


def clean_json(value):
    if isinstance(value, float) and not math.isfinite(value): return None
    if isinstance(value, dict): return {str(key): clean_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)): return [clean_json(item) for item in value]
    return value


def generate(root, comparator=REFERENCE):
    campaign = load(root / 'campaign.json', {})
    snapshot = load(root / 'live-status.json', {})
    manifest_path = root / 'outputs/manifest.json'
    manifest = load(manifest_path if manifest_path.exists() else root / 'manifest.json', {}) or {}
    manifests = manifest.get('cases', {})
    expected = {f'{sample}_REP{replicate}' for sample, replicate in campaign.get('samples', [])}
    runs = campaign.get('runs', [])
    states = {run['name']: run for run in snapshot.get('runs', [])}
    ref = reference(comparator)
    cases = {}
    for run in runs:
        if Path(run['name']).name != run['name'] or run['name'] in ('.', '..'): raise ValueError('Unsafe campaign case name')
        record = manifests.get(run['name'], {})
        files, issues = files_for(root, run, record)
        coverage = {kind: set() for kind in LIBRARY_KINDS}
        present = set()
        for rel in files:
            kind = category(Path(rel))
            if kind and 'merged_library/' in rel:
                present.add(kind)
                if kind in LIBRARY_KINDS: coverage[kind].add(Path(rel).name.split('.mLb.')[0])
            if kind == 'versions': present.add(kind)
        gaps = ['Missing category: ' + kind for kind in sorted(REQUIRED - present)]
        gaps += [f'Missing {kind} libraries: ' + ', '.join(sorted(expected - samples)) for kind, samples in coverage.items() if expected - samples]
        observation = states.get(run['name'], {})
        if not record.get('workflow_id') or record['workflow_id'] != observation.get('workflow_id'):
            gaps.append('Collected artifacts belong to another workflow ID')
        if record.get('revision') != run.get('revision') or record.get('workflow_source_verified') is not True:
            gaps.append('Collected source revision is missing or unverified')
        if any(record.get(key) != run.get(key) for key in ('name', 'arm', 'aligner')):
            gaps.append('Collected case identity differs from campaign')
        if run.get('payload_sha256') and record.get('payload_sha256') != run['payload_sha256']:
            gaps.append('Collected launch payload differs from campaign')
        succeeded = (observation.get('status') == 'SUCCEEDED' and bool(observation.get('workflow_id')) and not observation.get('error')
                     and observation.get('workflow_source_verified') is True
                     and bool(run.get('revision')) and observation.get('revision') == run['revision'])
        cases[run['name']] = {'run': run, 'observation': observation, 'files': files,
            'issues': issues + gaps + list(record.get('errors') or []), 'collector_complete': record.get('complete') is True,
            'succeeded': succeeded}
    pairs = {}
    for aligner in sorted({run['aligner'] for run in runs}):
        arms = {run['arm']: cases[run['name']] for run in runs if run['aligner'] == aligner}
        left, right = arms.get('unfixed'), arms.get('fixed')
        pair = {'state': 'INCOMPLETE', 'files': [], 'gaps': []}
        if left and right:
            for rel in sorted(left['files'].keys() | right['files'].keys()):
                kind = category(Path(rel))
                if not kind: continue
                item = {'relative_path': rel, 'category': kind}
                if rel not in left['files'] or rel not in right['files']:
                    item['state'] = 'MISSING_UNFIXED' if rel not in left['files'] else 'MISSING_FIXED'
                else:
                    try:
                        a, b = left['files'][rel], right['files'][rel]
                        item['state'] = 'COMPARED'
                        if kind == 'counts':
                            item['result'] = compare_counts(a, b, ref)
                            if '.mLb.' in Path(rel).name and (set(item['result']['shared_samples']) != expected
                                or item['result']['baseline_only_samples'] or item['result']['other_only_samples']):
                                raise ValueError('Library consensus sample identities do not match the four-library campaign')
                            if not item['result']['baseline_intervals'] or not item['result']['other_intervals']:
                                raise ValueError('No observed consensus count intervals')
                        elif kind == 'bed': item['result'] = compare_bed(a, b)
                        else:
                            av, bv = parsed(a, kind), parsed(b, kind)
                            item.update(unfixed=av, fixed=bv, differences=differences(av, bv))
                    except (OSError, ValueError, IndexError, KeyError) as error:
                        item.update(state='PARSE_ERROR', error=str(error))
                pair['files'].append(item)
            pair['gaps'] = [f'{arm}: {issue}' for arm, case in arms.items() for issue in case['issues']]
            if not all(case['succeeded'] for case in arms.values()): pair['gaps'].append('Both API-observed workflows must be SUCCEEDED')
            if not all(case['collector_complete'] for case in arms.values()): pair['gaps'].append('Both artifact collections must be complete')
            if any(item['state'] != 'COMPARED' for item in pair['files']): pair['gaps'].append('Missing/unparsed matched artifacts remain')
            if not pair['files']: pair['gaps'].append('No artifacts compared')
            if not pair['gaps']: pair['state'] = 'COMPARED'
        else: pair['gaps'].append('Missing fixed or unfixed campaign arm')
        pairs[aligner] = pair
    identities = [case['observation'].get('workflow_id') for case in cases.values()]
    global_gaps = [] if len(identities) == 4 and all(identities) and len(set(identities)) == 4 else ['Four distinct recorded workflow IDs are required']
    if len(runs) != 4 or len(expected) != 4 or len(pairs) != 2: global_gaps.append('Expected four cases, four library identities and two aligners')
    complete = not global_gaps and all(pair['state'] == 'COMPARED' for pair in pairs.values())
    return clean_json({'schema': 'nf-verify/original-cohort-comparison/v1', 'observed_at': datetime.now(timezone.utc).isoformat(),
        'state': 'COMPLETE' if complete else 'INCOMPLETE', 'full_comparison_complete': complete,
        'expected_library_samples': sorted(expected), 'comparator': {'path': str(comparator), 'sha256': REFERENCE_SHA},
        'cases': {name: {key: value for key, value in case.items() if key != 'files'} for name, case in cases.items()},
        'pairs': pairs, 'gaps': global_gaps, 'limits': ['COMPLETE means the scoped comparison ran, not scientific PASS or proof of correctness.',
            'Exact differences are retained without tolerance. BAM bytes, bigWig signal, plots and biological interpretation are outside this comparator.',
            'Count rows use the verified coordinate/sample-key comparator; Geneid and BAM path/order are ignored. Duplicate keys/columns are rejected.',
            'BED reports exact-interval and merged-basepair Jaccard separately; featureCounts coordinates remain one-based.',
            'Flagstat rates use QC-passed mapped/total, primary-mapped/primary, duplicates/total; denominator zero is unknown.']})


def markdown(report):
    lines = ['# Original HIV cohort comparison', '', '**State: ' + report['state'] + '**. Completeness is not scientific PASS.', '',
             'Expected libraries: ' + ', '.join(report.get('expected_library_samples', [])), '']
    lines += ['- ' + gap for gap in report.get('gaps', [])]
    for aligner, pair in report.get('pairs', {}).items():
        lines += ['## ' + aligner.upper() + ': ' + pair['state'], '']
        lines += ['- ' + gap for gap in pair['gaps']]
        lines += ['', '| Published path | Kind | Observation |', '|---|---|---|']
        for item in pair['files']:
            result, observation = item.get('result', {}), item['state']
            if item['category'] == 'counts' and result:
                observation += f"; {len(result['changed_cells'])} changed cells; {result['only_baseline']}/{result['only_other']} unique intervals; versions {result['baseline_version']} → {result['other_version']}"
            elif item['category'] == 'bed' and result:
                observation += f"; exact Jaccard {result['exact_interval_jaccard']}; bp Jaccard {result['basepair_jaccard']}"
            elif 'differences' in item: observation += f"; {len(item['differences'])} exact field differences"
            if item['category'] == 'versions' and 'unfixed' in item:
                for tool in sorted(item['unfixed'].keys() | item['fixed'].keys()):
                    if 'trim' in tool.lower() or 'cutadapt' in tool.lower():
                        observation += f"; {tool} {item['unfixed'].get(tool)} → {item['fixed'].get(tool)}"
            if item.get('error'): observation += '; ' + item['error']
            lines.append(f"| {item['relative_path']} | {item['category']} | {observation} |")
        lines.append('')
    lines += ['Full field/cell differences and recorded software versions are in `comparison.json`.', '', '## Limits', '']
    lines += ['- ' + error for error in report.get('errors', [])]
    lines += ['- ' + limit for limit in report.get('limits', [])]
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--count-comparator', type=Path, default=REFERENCE)
    args = parser.parse_args()
    try:
        report, code = generate(args.root, args.count_comparator), 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        report, code = {'state': 'ERROR', 'full_comparison_complete': False, 'errors': [str(error)]}, 2
    args.root.mkdir(parents=True, exist_ok=True)
    (args.root / 'comparison.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    (args.root / 'COMPARISON.md').write_text(markdown(report))
    print(json.dumps({'state': report['state'], 'full_comparison_complete': report['full_comparison_complete']}))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
