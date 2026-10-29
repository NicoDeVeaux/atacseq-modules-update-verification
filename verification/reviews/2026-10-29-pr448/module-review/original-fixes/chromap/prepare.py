import argparse
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('case', choices=('baseline', 'proposed'))
parser.add_argument('--source', type=Path)
args = parser.parse_args()
default = '${WORKTREE_ROOT}/atacseq-pr448-review/base' if args.case == 'baseline' else '${WORKTREE_ROOT}/atacseq-pr448-proposed-fix'
source = (args.source or Path(default)).resolve(strict=True)
folder = root / 'runs' / args.case
folder.mkdir(parents=True, exist_ok=True)
workflow = (source / 'workflows/atacseq.nf').read_text()
start = workflow.index('    ch_genome_bam\n        .map {')
end_marker = '        .set { ch_sort_bam }'
end = workflow.index(end_marker, start) + len(end_marker)
merge_wiring = workflow[start:end]
imports = f'include {{ PICARD_MERGESAMFILES as PICARD_MERGESAMFILES_LIBRARY }} from "{source}/modules/nf-core/picard/mergesamfiles/main"\n'
imports += f'include {{ PICARD_MARKDUPLICATES }} from "{source}/modules/nf-core/picard/markduplicates/main"\n'
if args.case == 'proposed':
    imports += f'include {{ PICARD_ADDORREPLACEREADGROUPS }} from "{source}/modules/nf-core/picard/addorreplacereadgroups/main"\n'
    chromap_stage = 'PICARD_ADDORREPLACEREADGROUPS(bams, reference)\n    ch_bam = PICARD_ADDORREPLACEREADGROUPS.out.bam'
    mark_call = 'PICARD_MARKDUPLICATES(bams, reference)'
else:
    chromap_stage = 'ch_bam = bams'
    mark_call = 'PICARD_MARKDUPLICATES(bams, reference.map { meta, fasta, fai -> [meta, fasta] }, reference.map { meta, fasta, fai -> [meta, fai] })'
main = (root / 'workflow.nf.in').read_text()
for name, value in [('IMPORTS', imports), ('CHROMAP_STAGE', chromap_stage), ('MARK_CALL', mark_call), ('MERGE_WIRING', merge_wiring)]:
    main = main.replace(f'@@{name}@@', value)
(folder / 'main.nf').write_text(main)
override = ''
if args.case == 'baseline':
    override = "process {\n withName: 'PICARD_MERGESAMFILES_LIBRARY|PICARD_MARKDUPLICATES' {\n  container = 'quay.io/biocontainers/picard:3.1.1--hdfd78af_0'\n }\n}\n"
config = (root / 'nextflow.config.in').read_text().replace('@@SOURCE@@', str(source)).replace('@@BASE_IMAGE_OVERRIDE@@', override)
(folder / 'nextflow.config').write_text(config)
paths = ['workflows/atacseq.nf', 'conf/modules.config', 'modules/nf-core/picard/mergesamfiles/main.nf', 'modules/nf-core/picard/markduplicates/main.nf']
if args.case == 'proposed':
    paths.append('modules/nf-core/picard/addorreplacereadgroups/main.nf')
(folder / 'source-used.json').write_text(json.dumps({'case': args.case, 'source': str(source), 'files': {p: hashlib.sha256((source / p).read_bytes()).hexdigest() for p in paths}, 'merge_wiring': merge_wiring}, indent=2) + '\n')
print(f'Prepared {args.case} from {source}')
