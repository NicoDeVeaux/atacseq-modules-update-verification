import json
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parent
summary={}
for case, expected in [('base',1),('current',0),('fixed',1)]:
    log=(root/f'{case}.run.out').read_text()
    metrics=Path(next(line.removeprefix('METRICS ') for line in log.splitlines() if line.startswith('METRICS ')))
    bam=Path(next(line.removeprefix('OUTPUT ') for line in log.splitlines() if line.startswith('OUTPUT ')))
    lines=metrics.read_text().splitlines()
    idx=next(i for i,line in enumerate(lines) if line.startswith('LIBRARY\t'))
    rows=[]
    for line in lines[idx+1:]:
        if not line.strip(): break
        rows.append(dict(zip(lines[idx].split('\t'),line.split('\t'))))
    pairs=sum(int(row['READ_PAIRS_EXAMINED']) for row in rows)
    duplicates=sum(int(row['READ_PAIR_DUPLICATES']) for row in rows)
    assert pairs==2 and duplicates==expected, (case,rows)
    result=subprocess.run(['docker','--context','colima','run','--rm',
        '-v',f'{bam.parent}:/data:ro','-w','/data',
        'community.wave.seqera.io/library/htslib_samtools:1.23.1--5b6bb4ede7e612e5',
        'samtools','view','-c','-F','0x400',bam.name],check=True,capture_output=True,text=True)
    retained=int(result.stdout.strip())
    assert retained==2*(2-expected), (case,retained)
    summary[case]={'libraries':[row['LIBRARY'] for row in rows], 'read_pairs_examined':pairs,
        'duplicate_pairs':duplicates,'reads_after_duplicate_filter':retained,'metrics':str(metrics),'bam':str(bam)}
(root/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
for case,value in summary.items():
    print(f"{case}: {value['duplicate_pairs']}/2 duplicate pairs; {value['reads_after_duplicate_filter']} reads retained after duplicate filtering")
