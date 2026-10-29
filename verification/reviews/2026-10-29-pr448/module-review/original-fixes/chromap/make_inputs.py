from pathlib import Path

root = Path(__file__).resolve().parent
(root / 'inputs').mkdir(exist_ok=True)
for replicate in (1, 2):
    for lane in (1, 2):
        name = f'rep{replicate}_lane{lane}'
        seq, quality = 'A' * 50, 'I' * 50
        text = '@HD\tVN:1.6\tSO:coordinate\n@SQ\tSN:chr1\tLN:1000\n'
        text += f'{name}\t99\tchr1\t100\t60\t50M\t=\t200\t150\t{seq}\t{quality}\n'
        text += f'{name}\t147\tchr1\t200\t60\t50M\t=\t100\t-150\t{seq}\t{quality}\n'
        (root / 'inputs' / f'{name}.sam').write_text(text)
