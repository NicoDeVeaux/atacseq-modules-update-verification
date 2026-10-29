import argparse
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('case', choices=('baseline', 'proposed'))
args = parser.parse_args()
folder = root / 'runs' / args.case
outputs, metrics = {}, {}
for line in (folder / 'run.out').read_text().splitlines():
    if line.startswith('OUTPUT\t') or line.startswith('METRICS\t'):
        kind, identifier, path = line.split('\t', 2)
        target = outputs if kind == 'OUTPUT' else metrics
        assert identifier not in target, (kind, identifier)
        target[identifier] = Path(path)
expected_ids = {'SAMPLE_A_REP1', 'SAMPLE_A_REP2'}
assert set(outputs) == set(metrics) == expected_ids, (outputs, metrics)
summary = {}
for identifier in sorted(expected_ids):
    bam = outputs[identifier]
    result = subprocess.run(['docker', '--context', 'colima', 'run', '--rm', '-v', f'{bam.parent}:/data:ro', '-w', '/data', 'community.wave.seqera.io/library/htslib_samtools:1.23.1--5b6bb4ede7e612e5', 'samtools', 'view', '-h', bam.name], check=True, capture_output=True, text=True)
    readgroups, records = {}, []
    for line in result.stdout.splitlines():
        if line.startswith('@RG\t'):
            fields = dict(item.split(':', 1) for item in line.split('\t')[1:])
            assert fields['ID'] not in readgroups
            readgroups[fields['ID']] = fields
        elif line and not line.startswith('@'):
            fields = line.split('\t')
            tags = {item.split(':', 2)[0]: item.split(':', 2)[2] for item in fields[11:]}
            records.append({'name': fields[0], 'flag': int(fields[1]), 'RG': tags.get('RG')})
    assert len(records) == 4, (identifier, records)
    assert sum(bool(record['flag'] & 0x400) for record in records) == 2, (identifier, records)
    lines = metrics[identifier].read_text().splitlines()
    index = next(i for i, line in enumerate(lines) if line.startswith('LIBRARY\t'))
    rows = []
    for line in lines[index + 1:]:
        if not line.strip():
            break
        rows.append(dict(zip(lines[index].split('\t'), line.split('\t'))))
    assert len(rows) == 1 and int(rows[0]['READ_PAIRS_EXAMINED']) == 2 and int(rows[0]['READ_PAIR_DUPLICATES']) == 1, rows
    if args.case == 'proposed':
        assert set(readgroups) == {identifier + '_T1', identifier + '_T2'}, readgroups
        assert {group['LB'] for group in readgroups.values()} == {identifier}, readgroups
        assert {group['SM'] for group in readgroups.values()} == {identifier}, readgroups
        assert {record['RG'] for record in records} == set(readgroups), records
        assert rows[0]['LIBRARY'] == identifier, rows
    else:
        assert not readgroups and {record['RG'] for record in records} == {None}, readgroups
        assert rows[0]['LIBRARY'] == 'Unknown Library', rows
    summary[identifier] = {'read_pairs_examined': 2, 'duplicate_pairs': 1, 'retained_reads': 2, 'readgroups': readgroups, 'records': records, 'metrics': str(metrics[identifier]), 'bam': str(bam)}
assert outputs['SAMPLE_A_REP1'] != outputs['SAMPLE_A_REP2']
if args.case == 'proposed':
    libraries = [{g['LB'] for g in summary[i]['readgroups'].values()} for i in sorted(expected_ids)]
    assert libraries[0].isdisjoint(libraries[1]), libraries
(folder / 'result.json').write_text(json.dumps(summary, indent=2) + '\n')
print(f'PASS {args.case}: two biological replicates remain separate; each has one cross-run duplicate pair and two retained reads; ' + ('technical RGIDs distinct and library IDs correctly shared within each replicate' if args.case == 'proposed' else 'historical no-RG baseline'))
