from pathlib import Path
import gzip

root = Path(__file__).parent / 'poly-inputs'
root.mkdir(exist_ok=True)
middle = 'ATACGTGCTACTGACTAGCATGTACGTAGCTACGATCGTACGCTAGCTAGCATAGTACGTACGT'
for mate in (1, 2):
    with gzip.open(root / f'poly_{mate}.fastq.gz', 'wt') as stream:
        for index in range(100):
            seq = middle + 'G' * 20 if mate == 1 else 'C' * 20 + middle
            stream.write(f'@read{index}/{mate}\n{seq}\n+\n' + 'I' * len(seq) + '\n')
