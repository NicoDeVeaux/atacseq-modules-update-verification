"""Offline assertions over actual saved tool output; does not run containers."""
from pathlib import Path
import collections
import hashlib
import json

ROOT = Path(__file__).resolve().parent


def load(path):
    return json.loads((ROOT / path).read_text())


def sam(path, tags=False):
    result = []
    for line in (ROOT / path).read_text().splitlines():
        if line.startswith('@'):
            continue
        fields = line.split('\t')
        result.append(tuple(fields[:11] + (sorted(fields[11:]) if tags else [])))
    return collections.Counter(result)


def main():
    source_count = 0
    for source in (ROOT / 'primary').glob('*.json'):
        data = json.loads(source.read_text())
        if isinstance(data, dict) and isinstance(data.get('content'), str) and 'sha' in data:
            content = data['content'].encode()
            assert hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest() == data['sha']
            assert source.with_suffix('.txt').read_bytes() == content
            source_count += 1
    assert source_count == 10
    for record in load('pipeline/pins.json'):
        raw = (ROOT / 'pipeline' / record['case'] / record['path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == record['sha256']
        assert hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == record['git_blob']
    for record in load('macs3-same-bam/run-results.json') + load('chromap-residual-pair/run-results.json') + load('chromap-5000-pairs/run-results.json'):
        assert record['exit_code'] == 0
    mapper_runs = load('bwa-bowtie-same-reads/run-results.json')
    assert len(mapper_runs['index']) == 3 and len(mapper_runs['align']) == 6
    assert all(x['exit_code'] == 0 for x in mapper_runs['index'] + mapper_runs['align'])
    for case, count in [('broad_no_control', 1431), ('narrow_no_control', 1150), ('broad_with_control', 1)]:
        extension = 'narrowPeak' if case.startswith('narrow') else 'broadPeak'
        old = ROOT / 'macs3-same-bam' / '3.0.1' / case
        new = ROOT / 'macs3-same-bam' / '3.0.4' / case
        assert (old / f'controlled_peaks.{extension}').read_bytes() == (new / f'controlled_peaks.{extension}').read_bytes()
        assert len((old / f'controlled_peaks.{extension}').read_text().splitlines()) == count
        def numeric_xls(folder):
            return [line for line in (folder / 'controlled_peaks.xls').read_text().splitlines() if line and not line.startswith('#')]
        assert numeric_xls(old) == numeric_xls(new)
        if extension == 'broadPeak':
            a = [x.split('\t') for x in (old / 'controlled_peaks.gappedPeak').read_text().splitlines()]
            b = [x.split('\t') for x in (new / 'controlled_peaks.gappedPeak').read_text().splitlines()]
            assert len(a) == len(b) == count
            assert all(x[:6] + x[8:] == y[:6] + y[8:] and y[6:8] == ['0', '0'] for x, y in zip(a, b))
    pairs = load('chromap-residual-pair/run-results.json')
    assert {(x['version'], x['fixture']): x['sam_records'] for x in pairs} == {('0.2.4', 'two_actual_pairs'): 2, ('0.2.4', 'unequal_pair_only'): 0, ('0.3.2', 'two_actual_pairs'): 4, ('0.3.2', 'unequal_pair_only'): 2}
    assert sam('chromap-5000-pairs/0.2.4/alignments.sam') == sam('chromap-5000-pairs/0.3.2/alignments.sam')
    assert load('chromap-5000-pairs/tag-differences.json')['changed_tag_counts'] == {'MD': 92}
    comparisons = load('bwa-bowtie-same-reads/comparison.json')
    assert comparisons[0]['alignment_core_multisets_equal'] and comparisons[0]['pipeline_F_0x100_core_equal']
    assert comparisons[0]['new_optional_tag_counts'] == {'MQ': 10003}
    for comparison in comparisons[1:]:
        assert comparison['alignment_core_multisets_equal'] and comparison['all_optional_fields_equal']
    base = sam('bwa-bowtie-same-reads/bowtie_2.5.2_index_2.4.4/alignments.sam', tags=True)
    for version, index in [('2.5.4', '2.5.4'), ('2.5.2', '2.5.4'), ('2.5.4', '2.4.4')]:
        assert sam(f'bwa-bowtie-same-reads/bowtie_{version}_index_{index}/alignments.sam', tags=True) == base
    print('PASS: 21 successful local tool commands; 10 primary source blobs; 18 pipeline source pins; saved scientific and metadata witnesses verified offline')


if __name__ == '__main__':
    main()
