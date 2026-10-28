from pathlib import Path
root=Path(__file__).resolve().parent
(root/'inputs').mkdir(exist_ok=True)
for lane in (1,2):
    seq='A'*50
    qual='I'*50
    name=f'read{lane}'
    text='@HD\tVN:1.6\tSO:coordinate\n@SQ\tSN:chr1\tLN:1000\n'
    text+=f'{name}\t99\tchr1\t100\t60\t50M\t=\t200\t150\t{seq}\t{qual}\n'
    text+=f'{name}\t147\tchr1\t200\t60\t50M\t=\t100\t-150\t{seq}\t{qual}\n'
    (root/'inputs'/f'lane{lane}.sam').write_text(text)
