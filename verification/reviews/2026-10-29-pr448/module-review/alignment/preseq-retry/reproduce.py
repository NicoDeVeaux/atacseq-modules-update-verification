#!/usr/bin/env python3
"""Exercise the actual PRESEQ retry wrapper using an argv-checking stand-in."""
from pathlib import Path
import hashlib,json,os,subprocess

ROOT=Path(__file__).resolve().parent
SOURCE=Path('REVIEW_HOME/Dev/atacseq-worktrees/atacseq-pr448-review/source')
JAR=Path('REVIEW_HOME/.nextflow/framework/26.04.6/nextflow-26.04.6-one.jar')
JAVA=Path('REVIEW_HOME/.sdkman/candidates/java/current/bin/java')
MODULE='modules/nf-core/preseq/lcextrap/main.nf'
PINS={'base':'4177ea95c56e15fdbdc52f6e210c3329ff69167b','dev':'73155d2b59d37f521e3f00228d559031d2e7847f'}

def main():
    sources={case:subprocess.check_output(['git','show',pin+':'+MODULE],cwd=SOURCE) for case,pin in PINS.items()}
    needle=b"args.join(' -defects')"
    if sources['dev'].count(needle)!=1:raise ValueError('Expected exact retry expression once')
    sources['proposed_append']=sources['dev'].replace(needle,b'"${args} -defects"')
    bins=ROOT/'bin';bins.mkdir(exist_ok=True)
    fake='''#!/usr/bin/env python3
import json,os,sys
from pathlib import Path
args=sys.argv[1:]
if not args:
 print('preseq Version: 3.2.0',file=sys.stderr);raise SystemExit(0)
with open(os.environ['PRESEQ_ARGV_RECORD'],'a') as f:f.write(json.dumps({'argv':args})+'\\n')
if not all(x in args for x in ['-verbose','-bam','-seed','1']):
 print('fixture: required original options lost',file=sys.stderr);raise SystemExit(43)
if '-defects' not in args:
 print('fixture: simulate initial defect failure',file=sys.stderr);raise SystemExit(42)
Path(args[args.index('-output')+1]).write_text('fixture complexity estimate\\n')
'''
    (bins/'preseq').write_text(fake);(bins/'preseq').chmod(0o755)
    env={key:os.environ[key] for key in ('HOME','PATH','JAVA_HOME','LANG') if key in os.environ}
    env.update(PATH=str(bins)+':'+env.get('PATH','/usr/bin:/bin'),NXF_OFFLINE='true',NXF_ANSI_LOG='false',NXF_DISABLE_CHECK_LATEST='true')
    results={}
    for case,body in sources.items():
        folder=ROOT/case
        if folder.exists():raise ValueError('Refusing to overwrite prior case')
        folder.mkdir();(folder/'module.nf').write_bytes(body);(folder/'input.bam').write_bytes(b'fixture; argv contract only\n')
        (folder/'main.nf').write_text("include { PRESEQ_LCEXTRAP } from './module'\nworkflow { PRESEQ_LCEXTRAP(Channel.of([[id:'library', single_end:false],file('input.bam')])) }\n")
        (folder/'nextflow.config').write_text("process { executor='local'; cpus=1; memory='1 GB'; maxRetries=1; maxErrors=-1; errorStrategy='finish'; ext.args='-verbose -bam -seed 1'; withLabel:error_ignore { errorStrategy='ignore' }; withLabel:error_retry { errorStrategy='retry'; maxRetries=2 } }\nconda.enabled=false\ndocker.enabled=false\nnextflow.enable.telemetry=false\n")
        record=folder/'argv.jsonl'
        cmd=[str(JAVA),'-jar',str(JAR),'run','main.nf','-ansi-log','false','-with-trace','trace.tsv','-work-dir','work']
        proc=subprocess.run(cmd,cwd=folder,env={**env,'PRESEQ_ARGV_RECORD':str(record)},stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
        (folder/'run.out').write_bytes(proc.stdout)
        argv=[json.loads(line)['argv'] for line in record.read_text().splitlines()] if record.exists() else []
        results[case]={'exit_code':proc.returncode,'invocations':argv,'source_sha256':hashlib.sha256(body).hexdigest(),'source_commit':PINS.get(case),'fixture':'Actual source wrapper; fake executable; no scientific computation'}
    results['gates']={
        'base_ignores_failed_optional_estimate':results['base']['exit_code']==0 and len(results['base']['invocations'])==1,
        'dev_loses_original_args_on_retry':len(results['dev']['invocations'])==3 and all('-bam' not in argv and '-seed' not in argv for argv in results['dev']['invocations'][1:]),
        'dev_fails_workflow':results['dev']['exit_code']!=0,
        'append_preserves_args_and_recovers':results['proposed_append']['exit_code']==0 and len(results['proposed_append']['invocations'])==2 and all('-bam' in argv and '-seed' in argv for argv in results['proposed_append']['invocations']) and '-defects' in results['proposed_append']['invocations'][1],
    }
    (ROOT/'result.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps({'gates':results['gates'],'report':str(ROOT/'result.json')}))
    raise SystemExit(0 if all(results['gates'].values()) else 1)

if __name__=='__main__':main()
