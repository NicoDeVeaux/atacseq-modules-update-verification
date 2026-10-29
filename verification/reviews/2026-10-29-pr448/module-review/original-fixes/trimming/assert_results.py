from pathlib import Path
import argparse
import gzip
import hashlib
import json
import re
import shlex

ROOT = Path(__file__).resolve().parent


def reads(label):
    source_record = json.loads((ROOT / label / 'source-evidence.json').read_text())
    for path, digest in source_record['sha256'].items():
        assert hashlib.sha256((Path(source_record['source']) / path).read_bytes()).hexdigest() == digest, ('source changed during validation', label, path)
    result = {}
    for mate in (1, 2):
        with gzip.open(ROOT / label / 'outputs' / f'poly_{mate}_val_{mate}.fq.gz', 'rt') as stream:
            lines = stream.read().splitlines()
        assert len(lines) == 400, (label, mate, len(lines))
        result[str(mate)] = [lines[index:index + 4] for index in range(0, len(lines), 4)]
        assert all(len(row[1]) == len(row[3]) for row in result[str(mate)])
    return result


def latest_command(label):
    paths = list((ROOT / label / 'work').glob('*/*/.command.sh'))
    assert paths, label
    return max(paths, key=lambda path: path.stat().st_mtime_ns).read_text()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=['baseline', 'proposed'])
    args = parser.parse_args()
    base = reads('baseline')
    assert all(row[1].endswith('G' * 20) for row in base['1'])
    assert all(row[1].startswith('C' * 20) for row in base['2'])
    assert '0.6.10' in (ROOT / 'baseline/tool-version.txt').read_text()
    negative = reads('negative-2.1')
    assert all(old[1][:-20] == new[1] for old, new in zip(base['1'], negative['1']))
    assert all(old[1][20:] == new[1] for old, new in zip(base['2'], negative['2']))
    assert '2.1.0' in (ROOT / 'negative-2.1/tool-version.txt').read_text()
    if args.phase == 'baseline':
        (ROOT / 'baseline-comparison.json').write_text(json.dumps({'base_version': '0.6.10', 'negative_control_version': '2.1.0', 'pairs': 100, 'negative_r1_bases_removed': 20, 'negative_r2_bases_removed': 20}, indent=2) + '\n')
        print('PASS baseline: 0.6.10 preserves both 100-read mates; 2.1.0 negative control loses 20 R1 terminal G and 20 R2 leading C bases per read.')
    else:
        proposed = reads('proposed')
        assert proposed == base, 'Proposed default differs from base FASTQ records'
        version = (ROOT / 'proposed/tool-version.txt').read_text().strip()
        assert re.search(r'(?<![0-9.])2\.3\.0(?![0-9.])', version), version
        command = latest_command('proposed')
        tokens = shlex.split(command.replace('\\\n', ' '))
        assert '--no_poly_g' in tokens, 'The actual proposed task did not pass --no_poly_g'
        result = {'pairs': 100, 'base_version': '0.6.10', 'proposed_version': version, 'fastq_records_identical': True, 'r2_leading_c_preserved': 20, 'actual_task_no_poly_g': True, 'negative_control_reproduced': True}
        (ROOT / 'comparison.json').write_text(json.dumps(result, indent=2) + '\n')
        print('PASS proposed: actual Trim Galore 2.3.0 task passes --no_poly_g; both 100-read mates exactly match pre-448 FASTQ records, including R2 leading C bases. Negative 2.1.0 control remains different.')
