#!/usr/bin/env python3
"""Verify the frozen public files and targeted scientific witnesses offline."""
from pathlib import Path
import collections
import gzip
import hashlib
import json
import re
import struct

ROOT = Path(__file__).resolve().parent


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load(path):
    return json.loads((ROOT / path).read_text())


def bam(path):
    raw = gzip.decompress((ROOT / path).read_bytes())
    assert raw[:4] == b'BAM\1'
    length = struct.unpack_from('<i', raw, 4)[0]
    header = raw[8:8 + length].decode()
    offset = 8 + length
    refs = struct.unpack_from('<i', raw, offset)[0]
    offset += 4
    for _ in range(refs):
        size = struct.unpack_from('<i', raw, offset)[0]
        offset += 4 + size + 4
    groups = {}
    for line in header.splitlines():
        if line.startswith('@RG\t'):
            fields = dict(item.split(':', 1) for item in line.split('\t')[1:])
            assert fields['ID'] not in groups
            groups[fields['ID']] = fields
    records = []
    while offset < len(raw):
        size = struct.unpack_from('<i', raw, offset)[0]
        record = raw[offset + 4:offset + 4 + size]
        assert len(record) == size
        offset += 4 + size
        fields = struct.unpack_from('<iiBBHHHiiii', record)
        name_size, cigar_count, flag, sequence_size = fields[2], fields[5], fields[6], fields[7]
        name = record[32:32 + name_size - 1].decode()
        position = 32 + name_size + 4 * cigar_count + (sequence_size + 1) // 2 + sequence_size
        tags = {}
        widths = {'A': 1, 'c': 1, 'C': 1, 's': 2, 'S': 2, 'i': 4, 'I': 4, 'f': 4, 'd': 8}
        while position < len(record):
            tag = record[position:position + 2].decode()
            kind = chr(record[position + 2])
            position += 3
            if kind in {'Z', 'H'}:
                end = record.index(b'\0', position)
                tags[tag] = record[position:end].decode()
                position = end + 1
            elif kind == 'B':
                subtype = chr(record[position])
                count = struct.unpack_from('<i', record, position + 1)[0]
                position += 5 + count * widths[subtype]
            else:
                position += widths[kind]
        assert position == len(record)
        records.append({'name': name, 'flag': flag, 'RG': tags.get('RG')})
    assert offset == len(raw)
    return groups, records


def fastq(path):
    lines = gzip.decompress((ROOT / path).read_bytes()).decode().splitlines()
    assert len(lines) == 400
    records = [lines[i:i + 4] for i in range(0, len(lines), 4)]
    assert all(x[0].startswith('@') and x[2].startswith('+') and len(x[1]) == len(x[3]) for x in records)
    return records


def main():
    manifest = load('PUBLIC-MANIFEST.json')
    actual = {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()}
    assert not any(p.is_symlink() for p in ROOT.rglob('*'))
    assert actual == set(manifest['files']) | {'PUBLIC-MANIFEST.json'}
    total = sum((ROOT / path).stat().st_size for path in actual)
    assert total < 15 * 1024 * 1024
    patterns = [b'/' + b'Users/', b'/' + b'private/tmp', b'/' + b'private/var/',
                rb'AKIA[0-9A-Z]{16}', rb'gh[pousr]_[A-Za-z0-9]{20,}',
                rb'(?i)authorization:\s*bearer\s+\S+', rb'(?i)x-amz-' + b'signature=',
                rb's3://[A-Za-z0-9][A-Za-z0-9._-]*/']
    for path, record in manifest['files'].items():
        raw = (ROOT / path).read_bytes()
        assert len(raw) <= 43 * 1024 * 1024
        assert digest(raw) == record['public_sha256'], path
        inspect = gzip.decompress(raw) if path.endswith(('.gz', '.bam')) else raw
        assert not any(re.search(pattern, inspect) for pattern in patterns), ('public-content pattern', path)
        if path.endswith('.bam'):
            header_size = struct.unpack_from('<i', inspect, 4)[0]
            assert digest(inspect[8 + header_size:]) == record['transformation']['post_header_payload_sha256']
            assert record['transformation']['post_header_payload_unchanged']
        if path.endswith(('.fastq.gz', '.fq.gz', '.sam')):
            assert record['original_sha256'] == record['public_sha256'], path
    for receipt, capture in load('SOURCE-CAPTURE-MAP.json').items():
        original = load(receipt)
        fingerprints = original.get('sha256', original.get('files'))
        for source, target in capture['files'].items():
            assert manifest['files'][target]['original_sha256'] == fingerprints[source]
            assert manifest['files'][target]['matches_execution_receipt_sha256'] == fingerprints[source]
    for mate in (1, 2):
        baseline = fastq(f'trimming/baseline/outputs/poly_{mate}_val_{mate}.fq.gz')
        proposed = fastq(f'trimming/proposed/outputs/poly_{mate}_val_{mate}.fq.gz')
        negative = fastq(f'trimming/negative-2.1/outputs/poly_{mate}_val_{mate}.fq.gz')
        assert baseline == proposed
        for old, changed in zip(baseline, negative):
            expected_sequence = old[1][:-20] if mate == 1 else old[1][20:]
            expected_quality = old[3][:-20] if mate == 1 else old[3][20:]
            assert changed == [old[0], expected_sequence, old[2], expected_quality]
            assert old[1].endswith('G' * 20) if mate == 1 else old[1].startswith('C' * 20)
    assert '0.6.10' in (ROOT / 'trimming/baseline/tool-version.txt').read_text()
    assert '2.1.0' in (ROOT / 'trimming/negative-2.1/tool-version.txt').read_text()
    assert '2.3.0' in (ROOT / 'trimming/proposed/tool-version.txt').read_text()
    proposed_commands = list((ROOT / 'trimming/proposed/work').glob('*/*/.command.sh'))
    assert len(proposed_commands) == 1 and '--no_poly_g' in proposed_commands[0].read_text()
    comparisons = load('trimming/comparison.json')
    assert comparisons['pairs'] == 100 and comparisons['fastq_records_identical'] and comparisons['negative_control_reproduced']
    for case in ['baseline', 'proposed']:
        results = load(f'chromap/runs/{case}/result.json')
        assert set(results) == {'SAMPLE_A_REP1', 'SAMPLE_A_REP2'}
        observed_libraries = []
        for identifier, result in results.items():
            prefix = f'chromap/runs/{case}/outputs/chromap/merged_library/'
            groups, records = bam(prefix + identifier + '.mLb.mkD.sorted.bam')
            assert groups == result['readgroups'] and records == result['records']
            assert len(records) == 4 and sum(bool(x['flag'] & 0x400) for x in records) == 2
            assert result['read_pairs_examined'] == 2 and result['duplicate_pairs'] == 1 and result['retained_reads'] == 2
            suffix = '.MarkDuplicates' if case == 'baseline' else ''
            metric = ROOT / (prefix + 'picard_metrics/' + identifier + '.mLb.mkD.sorted' + suffix + '.metrics.txt')
            lines = metric.read_text().splitlines()
            start = next(i for i, line in enumerate(lines) if line.startswith('LIBRARY\t'))
            row = dict(zip(lines[start].split('\t'), lines[start + 1].split('\t')))
            assert int(row['READ_PAIRS_EXAMINED']) == 2 and int(row['READ_PAIR_DUPLICATES']) == 1
            if case == 'proposed':
                assert set(groups) == {identifier + '_T1', identifier + '_T2'}
                assert {x['LB'] for x in groups.values()} == {identifier}
                assert {x['SM'] for x in groups.values()} == {identifier}
                assert {x['RG'] for x in records} == set(groups)
                observed_libraries.append({x['LB'] for x in groups.values()})
            else:
                assert not groups and {x['RG'] for x in records} == {None}
                assert row['LIBRARY'] == 'Unknown Library'
        if case == 'proposed':
            assert observed_libraries[0].isdisjoint(observed_libraries[1])
    exits = list(ROOT.rglob('.exitcode'))
    assert len(exits) == 15 and all(p.read_text().strip() == '0' for p in exits)
    print(json.dumps({'public_files': len(actual), 'bytes': total, 'source_receipts': 5,
                      'successful_task_exitcodes': len(exits), 'trimming_pairs': 100,
                      'constructed_libraries': 2, 'offline_checks': 'passed',
                      'new_scientific_runs': 0, 'network_access': False}))


if __name__ == '__main__':
    main()
