from pathlib import Path
import re

root = Path(__file__).parent
review = root.parent
for label, tree, disable in [('poly-nf-base', 'base', False), ('poly-nf-current', 'source', False), ('poly-nf-disabled', 'source', True)]:
    destination = root / label
    destination.mkdir(exist_ok=True)
    source_config = (review / tree / 'conf/modules.config').read_text()
    match = re.search(r"withName: 'TRIMGALORE' \{\s*ext.args\s*=\s*\{(.*?)\n\s*\}\s*publishDir", source_config, re.S)
    assert match, tree
    args = match.group(1)
    assert '--no_poly_g' not in args
    if disable:
        assert args.count(".join(' ').trim()") == 1
        args = args.replace(".join(' ').trim()", ".join(' ').trim() + ' --no_poly_g'")
    (destination / 'main.nf').write_text(f'''include {{ TRIMGALORE }} from '../../{tree}/modules/nf-core/trimgalore/main'
workflow {{
    TRIMGALORE(channel.of([[id: 'poly', single_end: false], [file("${{projectDir}}/../poly-inputs/poly_1.fastq.gz"), file("${{projectDir}}/../poly-inputs/poly_2.fastq.gz")]]))
    TRIMGALORE.out.reads.view()
}}
''')
    container_override = "container = 'quay.io/biocontainers/trim-galore:0.6.10--hdfd78af_2'" if tree == 'base' else ''
    (destination / 'nextflow.config').write_text('''params {
 trim_nextseq = 0
 clip_r1 = 0
 clip_r2 = 0
 three_prime_clip_r1 = 0
 three_prime_clip_r2 = 0
}
docker.enabled = true
docker.runOptions = '--platform linux/amd64'
process.executor = 'local'
process.cpus = 4
process.memory = '1 GB'
process {
 withName: TRIMGALORE {
''' + container_override + '\n' + 'ext.args = {' + args + '\n}\n' + '''publishDir = [path: "${projectDir}/outputs", mode: 'copy']
 }
}
''')
