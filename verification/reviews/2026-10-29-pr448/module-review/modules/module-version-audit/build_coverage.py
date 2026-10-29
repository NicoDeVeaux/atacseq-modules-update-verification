#!/usr/bin/env python3
"""Check coverage of every changed declared dependency and index the audit evidence."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORTS = {
    'software-alignment-qc.json': {'bowtie2', 'bwa', 'chromap', 'deeptools', 'picard', 'macs3', 'preseq', 'gffread'},
    'software-preprocessing.json': {'ataqv', 'khmer', 'subread', 'trim-galore', 'umi_tools', 'multiqc'},
    'software-system-tools.json': {'samtools', 'htslib', 'grep', 'sed', 'pigz', 'ucsc-bedgraphtobigwig', 'homer'},
}


def main():
    inventory = json.loads((ROOT / 'inventory.json').read_text())
    changes = {}
    for record in inventory['records']:
        if not record.get('old') or not record.get('new'):
            continue
        old = {dep['name']: dep['version_specifier'] for dep in record['old']['conda']['dependencies']}
        new = {dep['name']: dep['version_specifier'] for dep in record['new']['conda']['dependencies']}
        for name, value in new.items():
            if name in old and old[name] != value:
                change = changes.setdefault(name, {'old': set(), 'new': set(), 'components': set()})
                change['old'].add(old[name]); change['new'].add(value); change['components'].add(record['path'])
    rows = []
    for name, values in sorted(changes.items()):
        reports = [report for report, names in REPORTS.items() if name in names]
        assert len(reports) == 1, (name, reports)
        report = reports[0]
        data = json.loads((ROOT / report).read_text())
        assert data.get('tools'), report
        rows.append({'dependency': name, **{key: sorted(value) for key, value in values.items()},
            'upstream_scan': report})
    assert len(rows) == 16
    modules = json.loads((ROOT / 'nfcore-history.json').read_text())
    flows = json.loads((ROOT / 'nfcore-subworkflow-history.json').read_text())
    evidence = []
    for path in sorted(ROOT.iterdir()):
        if path.is_file() and path.name not in ('coverage.json', 'sha256sums.txt'):
            data = path.read_bytes()
            evidence.append({'path': path.name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    result = {'checked_on': '2026-10-28', 'pipeline_pr': 448,
        'base': inventory['base'], 'merge': inventory['merge'],
        'all_changed_component_files_accounted_for': inventory['counts']['changed_files_covered'],
        'inventory_components': inventory['counts']['records'],
        'changed_declared_dependencies_checked': len(rows), 'changed_dependencies': rows,
        'shared_module_paths_checked': len(modules['modules']),
        'shared_subworkflow_paths_checked': len(flows.get('subworkflows', [])),
        'limits': ['Source-declared pins; opaque images and full transitive package manifests not resolved',
                   'Bounded upstream release/history and pipeline-applicability scan',
                   'Known upstream fixes do not establish a new PR448 pipeline regression without reproduction',
                   'Some subsequent fixes were merged before pipeline PR448 itself merged',
                   'Full-data comparison remains in flight; its source is frozen'],
        'evidence': evidence}
    assert result['shared_module_paths_checked'] == 36
    assert result['shared_subworkflow_paths_checked'] == 7
    (ROOT / 'coverage.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: result[key] for key in ('all_changed_component_files_accounted_for',
        'inventory_components', 'changed_declared_dependencies_checked', 'shared_module_paths_checked',
        'shared_subworkflow_paths_checked')}))


if __name__ == '__main__':
    main()
