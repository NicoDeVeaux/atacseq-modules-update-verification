#!/usr/bin/env python3
"""Offline four-arm HIV report: final output requires verified complete evidence."""
import argparse
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import re
import sys

PINS = {'unfixed': '73155d2b59d37f521e3f00228d559031d2e7847f', 'fixed': 'a9b588235e4a1ceb3c8838acad430628c5737c86'}
ALIGNERS = ('bwa', 'chromap')
FLAGS = {'clN_total_reads': 'in total', 'clN_mapped_reads': 'mapped', 'clN_properly_paired_reads': 'properly paired', 'clN_duplicate_reads': 'duplicates'}
LABELS = {'raw_input_pairs': 'Raw input pairs', 'derived_input_pairs': 'Derived input pairs', 'clN_total_reads': 'Cleaned total reads',
          'clN_mapped_reads': 'Cleaned mapped reads', 'clN_properly_paired_reads': 'Cleaned properly paired reads',
          'clN_duplicate_reads': 'Cleaned duplicate-flagged reads', 'scale_factor': 'BigWig scale factor', 'macs3_peak_count': 'MACS3 peak count', 'frip': 'FRiP'}


class Incomplete(ValueError): pass


def load(path, default=None): return json.loads(path.read_text()) if path.exists() else default


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1048576), b''): digest.update(block)
    return digest.hexdigest()


def number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value): raise ValueError('Non-finite/non-numeric measurement')
    return value


def flagstat(path):
    result = {}
    for line in path.read_text().splitlines():
        match = re.fullmatch(r'(\d+)\s+\+\s+(\d+)\s+(.+)', line)
        if not match: raise ValueError('Invalid flagstat line')
        key = re.sub(r'\s+\((?:QC-passed reads.*|[^)]*%[^)]*|N/A[^)]*)\)$', '', match[3])
        if key in result: raise ValueError('Duplicate flagstat label')
        result[key] = {'passed': int(match[1]), 'failed': int(match[2]), 'total': int(match[1]) + int(match[2])}
    if not set(FLAGS.values()) <= result.keys(): raise ValueError('Missing flagstat metrics')
    return result


def scalar(raw, plot, sample):
    values = raw.get(plot, {}).get(sample)
    if not isinstance(values, dict) or len(values) != 1: raise ValueError('Missing/ambiguous MultiQC entry: ' + plot + '/' + sample)
    return number(next(iter(values.values())))


def raw_fastqc(multiqc, library, expected):
    sections = [data for headers, data in zip(multiqc.get('report_general_stats_headers', []), multiqc.get('report_general_stats_data', []))
                if headers.get('total_sequences', {}).get('namespace') == 'LIB: FastQC (raw)']
    if len(sections) != 1: raise ValueError('Missing/ambiguous namespace-labelled raw FastQC section')
    counts = []
    for mate in (1, 2):
        value = number(sections[0].get(f'{library}_T1_{mate}', {}).get('total_sequences'))
        if int(value) != value or value != expected: raise ValueError('Raw FastQC count differs from ENA for ' + library + ' mate ' + str(mate))
        counts.append(int(value))
    return counts


def identity(run, observed, collected, compared):
    issues = []
    if run.get('revision') != PINS.get(run.get('arm')): issues.append('Wrong campaign source pin')
    for label, record in [('observation', observed), ('collection', collected)]:
        if record.get('revision') != run.get('revision') or record.get('workflow_source_verified') is not True: issues.append(label + ': source unverified/mismatched')
    if not observed.get('workflow_id') or collected.get('workflow_id') != observed['workflow_id']: issues.append('Workflow ID mismatch')
    if any(collected.get(key) != run.get(key) for key in ('name', 'aligner', 'arm')): issues.append('Logical case mismatch')
    if collected.get('workflow_run_name') != run.get('run_name', run.get('name')): issues.append('Physical run-name mismatch')
    if not run.get('payload_sha256') or collected.get('payload_sha256') != run['payload_sha256']: issues.append('Launch payload hash mismatch')
    previous = compared.get('observation', {})
    if previous.get('workflow_id') != observed.get('workflow_id') or previous.get('revision') != run.get('revision'): issues.append('Comparison workflow/source identity mismatch')
    return issues


class Artifacts:
    def __init__(self, root, run, manifest, issue):
        self.root = root / 'outputs' / run['name']; self.files = {}; self.used = {}
        for record in manifest.get('files', []):
            rel = record.get('relative_path', ''); path = self.root / rel
            try:
                if not rel or Path(rel).is_absolute() or '..' in Path(rel).parts or path.is_symlink() or not path.resolve().is_relative_to(self.root.resolve()): raise ValueError('Unsafe artifact')
                if rel in self.files or record.get('status') != 'downloaded' or record.get('source_workflow_id') != manifest.get('workflow_id'): raise ValueError('Artifact identity/status mismatch')
                if path.stat().st_size != record.get('bytes') or sha(path) != record.get('sha256'): raise ValueError('Artifact byte/hash mismatch')
                self.files[rel] = path
            except (OSError, ValueError) as error: issue('error', rel + ': ' + str(error))

    def one(self, suffix):
        matches = [(rel, path) for rel, path in self.files.items() if rel.endswith(suffix)]
        if len(matches) != 1: raise ValueError(f'Expected one artifact ending {suffix}; found {len(matches)}')
        rel, path = matches[0]; self.used[rel] = sha(path)
        return path


def metrics(artifacts, prefix, sample, stage, multiqc, issue):
    result = {}
    try:
        split = flagstat(artifacts.one(prefix + f'/samtools_stats/{sample}.{stage}.clN.sorted.bam.flagstat'))
        result.update({key: split[label]['total'] for key, label in FLAGS.items()}); result['flagstat_qc_split'] = split
        value = float(artifacts.one(prefix + f'/bigwig/scale/{sample}.{stage}.clN.scale_factor.txt').read_text().strip())
        result['scale_factor'] = number(value)
    except (OSError, ValueError) as error: issue('error', str(error))
    for key, plot in [('macs3_peak_count', 'peak_count'), ('frip', 'frip_score')]:
        try: result[key] = scalar(multiqc.get('report_saved_raw_data', {}), f'multiqc_{"mlib" if stage == "mLb" else "mrep"}_{plot}-plot', sample)
        except ValueError as error: issue('warning', str(error))
    return result


def consensus(pair, group):
    result = []
    for item in pair.get('files', []):
        if group not in item['relative_path'] or item['category'] not in ('bed', 'counts'): continue
        value = item.get('result', {}); record = {'path': item['relative_path'], 'kind': item['category'], 'state': item['state']}
        if item['state'] == 'COMPARED' and value:
            if item['category'] == 'bed':
                record.update({k: value[k] for k in ('unfixed_intervals', 'fixed_intervals', 'shared_exact_intervals', 'exact_interval_jaccard', 'intersection_bp', 'union_bp', 'basepair_jaccard')})
                record.update(only_unfixed=len(value['only_unfixed']), only_fixed=len(value['only_fixed']))
            else:
                record.update({k: value[k] for k in ('baseline_version', 'other_version', 'baseline_intervals', 'other_intervals', 'shared_intervals', 'shared_samples', 'per_sample')})
                record['changed_count_cells'] = len(value['changed_cells'])
        result.append(record)
    return result


def generate(root, partial=False):
    comparison = load(root / 'comparison.json', {})
    if comparison.get('full_comparison_complete') is not True and not partial: raise Incomplete('Four-arm comparison incomplete; --partial permits an explicit preview')
    campaign, snapshot, manifest, ena = [load(root / p, {}) for p in ('campaign.json', 'live-status.json', 'outputs/manifest.json', 'hiv-input-provenance.json')]
    libraries = sorted(f'{s}_REP{r}' for s, r in campaign.get('samples', [])); groups = sorted({re.sub(r'_REP\d+$', '', lib) for lib in libraries})
    if len(libraries) != 4 or len(set(libraries)) != 4: raise ValueError('Expected four distinct libraries')
    inputs = [{'accession': r['accession'], 'library': re.sub(r'_T1_[12]$', '', r['saved_raw_fastqc_sample_names'][0]), 'ena_pairs': int(r['metadata']['read_count']),
               'archived_sequences_per_mate': r.get('saved_raw_fastqc_sequences_per_mate')} for r in ena.get('runs', [])]
    expected = {r['library']: r['ena_pairs'] for r in inputs}
    if set(expected) != set(libraries) or sum(expected.values()) != 87089251: raise ValueError('ENA provenance does not identify the full four-library cohort')
    report = {'state': 'PARTIAL' if partial else 'FINAL', 'observed_at': datetime.now(timezone.utc).isoformat(), 'comparison_observed_at': comparison.get('observed_at'),
        'status_observed_at': snapshot.get('observed_at'), 'full_comparison_complete': comparison.get('full_comparison_complete') is True,
        'libraries': libraries, 'groups': groups, 'inputs': inputs, 'cases': {}, 'aligners': {}, 'issues': []}
    def issue(level, text, case=None): report['issues'].append({'level': level, 'case': case, 'message': text})
    observations = {r['name']: r for r in snapshot.get('runs', [])}; runs = campaign.get('runs', [])
    if len(runs) != 4 or {(r['aligner'], r['arm']) for r in runs} != {(a, b) for a in ALIGNERS for b in PINS}: issue('error', 'Expected four aligner/arm cases')
    ids = [observations.get(r['name'], {}).get('workflow_id') for r in runs]
    if len(set(ids)) != 4 or not all(ids): issue('error', 'Expected four distinct current workflow IDs')
    for run in runs:
        name = run['name']; observed = observations.get(name, {}); collected = manifest.get('cases', {}).get(name, {})
        mark = lambda level, text: issue(level, text, name)
        for text in identity(run, observed, collected, comparison.get('cases', {}).get(name, {})): mark('error', text)
        if observed.get('status') != 'SUCCEEDED' or collected.get('complete') is not True: mark('error', 'Workflow/collection incomplete')
        artifacts = Artifacts(root, run, collected, mark); multiqc = {}
        try: multiqc = load(artifacts.one('/multiqc_data/multiqc_data.json'))
        except (OSError, ValueError) as error: mark('error', str(error))
        case = {'aligner': run['aligner'], 'arm': run['arm'], 'source_commit': run['revision'], 'workflow_id': observed.get('workflow_id'), 'url': observed.get('url'),
            'status': observed.get('status'), 'collection_complete': collected.get('complete') is True, 'verified_artifacts': len(artifacts.files), 'workflow_run_name': collected.get('workflow_run_name'),
            'libraries': {}, 'merged_replicates': {}, 'initial_workflow_id': run.get('initial_workflow_id'), 'payload_sha256': run.get('payload_sha256')}
        for lib in libraries:
            value = metrics(artifacts, run['aligner'] + '/merged_library', lib, 'mLb', multiqc, mark)
            try:
                value['raw_fastqc_reads_per_mate'] = raw_fastqc(multiqc, lib, expected[lib]); value['raw_input_pairs'] = value['raw_fastqc_reads_per_mate'][0]
            except ValueError as error: mark('error', str(error))
            case['libraries'][lib] = value
        if all('raw_input_pairs' in v for v in case['libraries'].values()): case['raw_input_pairs'] = sum(v['raw_input_pairs'] for v in case['libraries'].values())
        for group in groups:
            value = metrics(artifacts, run['aligner'] + '/merged_replicate', group, 'mRp', multiqc, mark)
            own = [v.get('raw_input_pairs') for lib, v in case['libraries'].items() if re.sub(r'_REP\d+$', '', lib) == group]
            value['derived_input_pairs'] = sum(own) if all(v is not None for v in own) else None; case['merged_replicates'][group] = value
        case['used_artifact_sha256'] = artifacts.used; report['cases'][name] = case
    for aligner in ALIGNERS:
        pair = comparison.get('pairs', {}).get(aligner, {})
        report['aligners'][aligner] = {'state': pair.get('state'), 'library_consensus': consensus(pair, 'merged_library/'), 'merged_replicate_consensus': consensus(pair, 'merged_replicate/')}
        if pair.get('state') != 'COMPARED': issue('error', aligner + ': paired comparison incomplete')
    report['history'] = {'ena_recovery': campaign.get('transport_recovery', {}), 'nextflow': campaign.get('nextflow_version'), 'blacklist_portability': bool(campaign.get('portability_correction'))}
    report['provenance'] = {p: sha(root / p) for p in ('campaign.json', 'comparison.json', 'live-status.json', 'outputs/manifest.json', 'hiv-input-provenance.json')}
    report['generator_sha256'] = sha(Path(__file__))
    if not partial and any(i['level'] == 'error' for i in report['issues']): raise Incomplete('Final report blocked by source/coverage/raw-count/parser errors; use --partial to inspect')
    return report


def display(value):
    return 'Unavailable' if value is None else f'{value:,}' if isinstance(value, int) else str(value)


def delta(left, right):
    if left is None or right is None: return 'Unavailable'
    value = Decimal(str(right)) - Decimal(str(left))
    return ('+' if value > 0 else '') + format(value, 'f')


def measurement_table(report, aligner, section, names, raw_key):
    cases = {c['arm']: c for c in report['cases'].values() if c['aligner'] == aligner}
    lines = ['| Library / group | Metric | Unfixed | Fixed | Δ |', '|---|---|---:|---:|---:|']
    for name in names:
        for key in [raw_key, *FLAGS, 'scale_factor', 'macs3_peak_count', 'frip']:
            a, b = [cases.get(arm, {}).get(section, {}).get(name, {}).get(key) for arm in ('unfixed', 'fixed')]
            lines.append(f'| {name} | {LABELS[key]} | {display(a)} | {display(b)} | {delta(a, b)} |')
    return lines


def outcome_summary(report):
    lines = ['', '## Outcome at a glance', '', '| Aligner | Cleaned reads unfixed | Cleaned reads fixed | Δ cleaned reads | Library consensus exact Jaccard | Covered-base Jaccard | Changed shared count cells |', '|---|---:|---:|---:|---:|---:|---:|']
    for aligner in ALIGNERS:
        cases = {case['arm']: case for case in report['cases'].values() if case['aligner'] == aligner}
        totals = []
        for arm in ('unfixed', 'fixed'):
            values = [cases.get(arm, {}).get('libraries', {}).get(lib, {}).get('clN_total_reads') for lib in report['libraries']]
            totals.append(sum(values) if values and all(value is not None for value in values) else None)
        consensus = report['aligners'][aligner]['library_consensus']
        bed = next((item for item in consensus if item['kind'] == 'bed' and item['state'] == 'COMPARED'), {})
        counts = next((item for item in consensus if item['kind'] == 'counts' and item['state'] == 'COMPARED'), {})
        lines.append(f"| {aligner.upper()} | {display(totals[0])} | {display(totals[1])} | {delta(*totals)} | {display(bed.get('exact_interval_jaccard'))} | {display(bed.get('basepair_jaccard'))} | {display(counts.get('changed_count_cells'))} |")
    return lines + ['', 'High covered-base overlap does not imply identical intervals or counts. Changed cells refer only to exact shared coordinates; nonshared intervals are reported separately.']


def markdown(report):
    lines = ['# Full-input HIV ATAC-seq comparison', '', f"**{report['state']}**. Generated {report['observed_at']}; comparison observed {report['comparison_observed_at']}.", '',
        'Reviewed dev pin [73155d](https://github.com/nf-core/atacseq/commit/' + PINS['unfixed'] + ') versus proposed fix [a9b588](https://github.com/NicoDeVeaux/atacseq-nfcore/commit/' + PINS['fixed'] + '). This is a fresh matched-source comparison, not a pre-448 replay or scientific PASS.', '',
        '**87,089,251 input pairs, four biological libraries, one technical run per library.** These runs do not isolate the cross-technical-run Chromap library-ID correction.', '',
        '| Aligner / arm | Workflow | Physical name | Status | Collection complete | Verified files |', '|---|---|---|---|---|---:|']
    for c in report['cases'].values():
        link = f"[{c['workflow_id']}]({c['url']})" if c['url'] else display(c['workflow_id'])
        lines.append(f"| {c['aligner']} / {c['arm']} | {link} | {c['workflow_run_name']} | {c['status']} | {c['collection_complete']} | {c['verified_artifacts']} |")
    lines += outcome_summary(report)
    lines += input_section(report)
    lines += settings_section(report)
    lines += ['', '## Measured outputs', '', 'Δ is fixed minus unfixed using exact decimal arithmetic. Flagstat values sum QC-passed and QC-failed **read records**, including properly paired records. JSON preserves both components. Merged-replicate inputs are derived sums. No tolerance-based acceptance is applied.']
    for aligner in ALIGNERS:
        lines += ['', '### ' + aligner.upper(), '', 'Per-library cleaned outputs:', ''] + measurement_table(report, aligner, 'libraries', report['libraries'], 'raw_input_pairs')
        lines += ['', 'Merged-replicate outputs:', ''] + measurement_table(report, aligner, 'merged_replicates', report['groups'], 'derived_input_pairs')
        lines += consensus_section(report, aligner)
    lines += limits_section(report)
    return '\n'.join(lines) + '\n'


def input_section(report):
    lines = ['', '## Input identity and full-input verification', '', '| Library | ENA run | ENA pairs | Archived raw reads per mate |', '|---|---|---:|---:|']
    for row in report['inputs']:
        lines.append(f"| {row['library']} | [{row['accession']}](https://www.ebi.ac.uk/ena/browser/view/{row['accession']}) | {row['ena_pairs']:,} | {display(row['archived_sequences_per_mate'])} |")
    lines += ['', 'Actual current-arm MultiQC is selected by the explicit **LIB: FastQC (raw)** namespace. Both mates of every library must exactly match ENA. Missing, ambiguous or mismatched counts block a final report.', '',
        '| Aligner / arm | Actual R1 / R2 counts per library | Total input pairs |', '|---|---|---:|']
    for case in report['cases'].values():
        values = '; '.join(lib + ': ' + ' / '.join(map(display, value.get('raw_fastqc_reads_per_mate', [None, None]))) for lib, value in case['libraries'].items())
        lines.append(f"| {case['aligner']} / {case['arm']} | {values} | {display(case.get('raw_input_pairs'))} |")
    return lines + ['', 'Archived counts/accessions agree with ENA. Matching counts do not establish byte identity between historical stored FASTQs and public ENA objects. Metadata MD5s and response/report hashes remain in `hiv-input-provenance.json`. No historical byte-for-byte replay is asserted.']


def settings_section(report):
    lines = ['', '## Matched settings and ENA recovery', '',
        'Chromap initial attempts encountered ENA transport/remote-existence failures. Campaign records preserve source-identical, same-arm resumes and unchanged scientific inputs/parameters; foreign-file transfer retries/concurrency changed to 8/2. Physical recovery names end `_r2`; logical keys and source pins stay stable. Initial failed attempts do not count as successful comparison arms.']
    for c in report['cases'].values():
        if c.get('initial_workflow_id'):
            url = c['url'].rsplit('/', 1)[0] + '/' + c['initial_workflow_id'] if c.get('url') else ''
            lines.append(f"- {c['aligner']} / {c['arm']}: initial [{c['initial_workflow_id']}]({url}) → current {c['workflow_id']}.")
    lines += ['', f"Nextflow {report['history']['nextflow']}. The old blacklist checkout path was replaced across all arms by an immutable URL for verified identical blacklist bytes."]
    evidence = report.get('parameter_evidence')
    if evidence:
        lines += ['', '| Aligner | Parameters per arm | Only parameter difference | Config equal | Compute / Nextflow equal |', '|---|---:|---|---|---|']
        for aligner, value in evidence['within_aligner'].items():
            lines.append(f"| {aligner} | {value['parameter_count']} | {', '.join(value['only_parameter_differences'])} | {value['config_equal']} | {value['compute_environment_equal']} / {value['nextflow_version_equal']} |")
        lines += ['', 'Common checked settings: ' + '; '.join(k + '=' + str(v) for k, v in evidence['common_settings'].items()) + '.', '',
            'This independent comparison checks reviewed prepared payloads and their exact hashes. API-observed commits and collection identities are verified separately. Supplied config concerns Chromap recovery transport and is equal within each pair. No private payload contents are embedded.']
    else: lines += ['', 'Sanitized independent launch-parameter comparison has not been supplied.']
    return lines


def consensus_section(report, aligner):
    lines = []
    for title, key in [('Library-derived consensus', 'library_consensus'), ('Merged-replicate-derived consensus', 'merged_replicate_consensus')]:
        lines += ['', title + ':', '']
        if not report['aligners'][aligner][key]: lines.append('- Unavailable.')
        for item in report['aligners'][aligner][key]:
            if item['state'] != 'COMPARED': lines.append(f"- `{item['path']}`: {item['state']}."); continue
            if item['kind'] == 'bed':
                lines.append(f"- BED: {item['unfixed_intervals']:,} → {item['fixed_intervals']:,} intervals; {item['shared_exact_intervals']:,} exact shared; only unfixed/fixed {item['only_unfixed']:,}/{item['only_fixed']:,}; exact interval Jaccard **{item['exact_interval_jaccard']}**; covered-base Jaccard **{item['basepair_jaccard']}**.")
            else:
                lines += [f"- Counts: **{item['changed_count_cells']:,} changed cells**, {item['shared_intervals']:,} shared coordinates; featureCounts {item['baseline_version']} → {item['other_version']}; columns: {', '.join(item['shared_samples'])}.", '',
                    '| Library | Total unfixed | Total fixed | Δ total | Changed shared intervals | Sum absolute Δ | Max absolute Δ |', '|---|---:|---:|---:|---:|---:|---:|']
                for row in item['per_sample']:
                    lines.append(f"| {row['sample']} | {row['baseline_total']:,} | {row['other_total']:,} | {row['total_delta']:+,} | {row['changed_intervals']:,} | {row['sum_abs_delta']:,} | {row['max_abs_delta']} |")
    return lines


def limits_section(report):
    bwa = next((r for r in report['aligners']['bwa']['library_consensus'] if r['kind'] == 'bed' and r['state'] == 'COMPARED'), None)
    observed = f" BWA library consensus has exact Jaccard {100*bwa['exact_interval_jaccard']:.2f}% versus covered-base Jaccard {100*bwa['basepair_jaccard']:.2f}%." if bwa else ''
    lines = ['', '## Interpretation, provenance and ambiguities', '',
        'High covered-base Jaccard does not mean identical intervals: shifted boundaries can preserve almost all covered bases while changing many exact interval keys.' + observed + ' These are measured differences, not equivalence.', '',
        'Count comparisons join coordinates and library names, ignoring unstable interval IDs and row/column order. Own-arm totals use each full interval set. Changed-cell statistics and any correlation use only exact shared coordinates; nonshared rows are excluded from those calculations and remain explicit in `comparison.json`.', '',
        'Peak counts/FRiP come only from unambiguous collected MultiQC `report_saved_raw_data` entries. Consensus summaries come from guarded `comparison.json`, which preserves full coordinate/cell differences. Individual library broadPeak coordinates are not assumed collected; BED overlap concerns consensus files.', '',
        'A separate review observed identical numeric BED/SAF starts in both source arms rather than explicit BED→SAF conversion. This is an unverified shared observation, not a newly confirmed bug, and is not attributed to PR448. No cross-format biological coordinate equivalence is asserted.', '',
        'BAM byte/read-name equality, BigWig signal comparison, plot interpretation, biological differential inference and proof that the pipeline is bug-free are outside scope. Success and comparison completeness establish execution/coverage.', '']
    lines += [f"- {item['level'].upper()} [{item['case'] or 'campaign'}]: {item['message']}" for item in report['issues']]
    if not report['issues']: lines.append('- No parser/source ambiguity was detected.')
    return lines + ['', 'Accompanying JSON retains full source pins, input/artifact hashes, QC splits, parameter-evidence hash and generator identity. No credentials, private payload contents or private source storage paths are embedded.']


def parameter_evidence(path, report):
    value = load(path)
    if value.get('source_pins') != PINS or value.get('payload_hashes_verified') is not True: raise ValueError('Parameter evidence source/hash verification missing')
    for aligner in ALIGNERS:
        own = value.get('within_aligner', {}).get(aligner, {})
        if own.get('parameter_count') != 41 or own.get('only_parameter_differences') != ['outdir'] or any(own.get(k) is not True for k in ('config_equal', 'compute_environment_equal', 'nextflow_version_equal')): raise ValueError('Parameter comparison differs from reviewed matched settings')
    if {p['case']: p['sha256'] for p in value.get('payloads', [])} != {name: case['payload_sha256'] for name, case in report['cases'].items()}: raise ValueError('Parameter evidence payload hashes differ from campaign')
    expected = {'read_length': 50, 'macs_gsize': 2701262066, 'keep_dups': False, 'mito_name': 'chrM', 'skip_multiqc': False}
    if value.get('common_settings') != expected: raise ValueError('Parameter common settings differ from reviewed values')
    return {key: value.get(key) for key in ('observed_at', 'source_pins', 'payload_hashes_verified', 'payloads', 'within_aligner', 'common_settings')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path); parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--partial', action='store_true'); parser.add_argument('--parameter-evidence', type=Path)
    args = parser.parse_args(); root, out = args.root.resolve(), args.out.resolve()
    if out.is_relative_to(root): parser.error('--out must be outside the canonical evidence root')
    try:
        report = generate(root, args.partial)
        if args.parameter_evidence:
            report['parameter_evidence'] = parameter_evidence(args.parameter_evidence, report)
            report['parameter_evidence_sha256'] = sha(args.parameter_evidence)
        elif not args.partial: raise Incomplete('Final report requires --parameter-evidence')
        out.mkdir(parents=True, exist_ok=True)
        md, js = ('PARTIAL-REPORT.md', 'partial-report.json') if args.partial else ('FINAL-REPORT.md', 'report.json')
        (out / md).write_text(markdown(report)); (out / js).write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
        print(json.dumps({'state': report['state'], 'report': str(out / md), 'issues': len(report['issues'])})); return 0
    except Incomplete as error: print(str(error), file=sys.stderr); return 3
    except (OSError, ValueError, KeyError, TypeError) as error: print('Report error: ' + str(error), file=sys.stderr); return 2


if __name__ == '__main__': sys.exit(main())
