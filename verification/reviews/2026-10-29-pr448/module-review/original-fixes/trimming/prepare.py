"""Build a wrapper around the selected real module and its exact pipeline arguments."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parent
REVIEW = ROOT.parents[1] / 'atacseq-pr448-review'
MIDDLE = 'ATACGTGCTACTGACTAGCATGTACGTAGCTACGATCGTACGCTAGCTAGCATAGTACGTACGT'


def fixture():
    inputs = ROOT / 'inputs'
    inputs.mkdir(exist_ok=True)
    for mate in (1, 2):
        with gzip.open(inputs / f'poly_{mate}.fastq.gz', 'wt') as stream:
            for index in range(100):
                sequence = MIDDLE + 'G' * 20 if mate == 1 else 'C' * 20 + MIDDLE
                stream.write(f'@read{index}/{mate}\n{sequence}\n+\n' + 'I' * len(sequence) + '\n')


def prepare(label, source):
    source = Path(source).resolve()
    selected = ROOT / label
    selected.mkdir(exist_ok=True)
    config = (source / 'conf/modules.config').read_text()
    match = re.search(r"withName: 'TRIMGALORE' \{\s*ext.args\s*=\s*\{(.*?)\n\s*\}\s*publishDir", config, re.S)
    if not match:
        raise SystemExit('Cannot identify the real TRIMGALORE ext.args; inspect manually')
    arguments = match.group(1)
    defaults = (source / 'nextflow.config').read_text()
    params = {}
    literal = re.compile(r'''^(?:null|true|false|[0-9]+(?:\.[0-9]+)?|'[^'\n]*'|"[^"\n]*")$''')
    for name in sorted(set(re.findall(r'params\.([A-Za-z0-9_]+)', arguments))):
        values = re.findall(r'^\s*' + re.escape(name) + r'\s*=\s*([^\n]+)', defaults, re.M)
        if len(values) != 1 or not literal.fullmatch(values[0].strip()):
            raise SystemExit(f'Cannot safely extract literal default for {name}; inspect manually')
        params[name] = values[0].strip()
    module = (source / 'modules/nf-core/trimgalore/main.nf').read_text()
    version_capture = ''
    if re.search(r'emit:\s*versions_trimgalore\b', module):
        version_capture = '''TRIMGALORE.out.versions_trimgalore.map { process, tool, version -> "${tool}=${version}" }.collectFile(name: 'tool-version.txt', storeDir: projectDir, newLine: true)
'''
    include = str(source / 'modules/nf-core/trimgalore/main')
    if any(character in include for character in "'\n\r"):
        raise SystemExit('Unsupported source path')
    (selected / 'main.nf').write_text(f'''include {{ TRIMGALORE }} from '{include}'
workflow {{
    TRIMGALORE(channel.of([[id: 'poly', single_end: false], [file("${{projectDir}}/../inputs/poly_1.fastq.gz"), file("${{projectDir}}/../inputs/poly_2.fastq.gz")]]))
    TRIMGALORE.out.reads.view()
    {version_capture}
}}
''')
    override = "container = 'quay.io/biocontainers/trim-galore:0.6.10--hdfd78af_2'" if label == 'baseline' else ''
    (selected / 'nextflow.config').write_text('params {\n' + ''.join(f' {key} = {value}\n' for key, value in params.items()) + '''}
docker.enabled = true
docker.runOptions = '--platform linux/amd64'
process.executor = 'local'
process.cpus = 4
process.memory = '1 GB'
process.time = '5m'
process {
 withName: TRIMGALORE {
''' + override + '\next.args = {' + arguments + '\n}\n' + '''publishDir = [path: "${projectDir}/outputs", mode: 'copy']
 }
}
''')
    paths = ['conf/modules.config', 'nextflow.config', 'modules/nf-core/trimgalore/main.nf', 'modules/nf-core/trimgalore/environment.yml']
    fingerprints = {path: hashlib.sha256((source / path).read_bytes()).hexdigest() for path in paths if (source / path).exists()}
    commit = subprocess.run(['git', '-C', str(source), 'rev-parse', 'HEAD'], capture_output=True, text=True)
    source_commit = commit.stdout.strip() if commit.returncode == 0 else None
    if label == 'baseline':
        source_commit = json.loads((REVIEW / 'pins.json').read_text())['commits']['base']
        for path in fingerprints:
            pinned = subprocess.run(['git', '-C', str(REVIEW / 'source'), 'show', source_commit + ':' + path], check=True, capture_output=True).stdout
            assert hashlib.sha256(pinned).hexdigest() == fingerprints[path], path
    if (source / '.git').exists():
        diff = subprocess.run(['git', '-C', str(source), 'diff', '--binary', 'HEAD', '--', *paths], check=True, capture_output=True).stdout
        (selected / 'source-diff.patch').write_bytes(diff)
    record = {'source': str(source), 'commit': source_commit, 'sha256': fingerprints, 'ext_args_verbatim': arguments, 'literal_defaults': params, 'container_override': override or None}
    (selected / 'source-evidence.json').write_text(json.dumps(record, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=['baseline', 'proposed'])
    parser.add_argument('--source', type=Path)
    args = parser.parse_args()
    fixture()
    if args.phase == 'baseline':
        prepare('baseline', REVIEW / 'base')
        prepare('negative-2.1', REVIEW / 'source')
    else:
        if args.source is None:
            parser.error('Proposed phase requires an explicitly selected --source')
        prepare('proposed', args.source)
