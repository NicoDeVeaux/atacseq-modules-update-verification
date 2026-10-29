#!/usr/bin/env python3
"""Compare archived HIV matrices with the new BWA arms using coordinate/sample keys."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path

HELPER_SHA='2c844a7aebea68007358064fb31fa14742758a87d133d979bc57d9a8eca95ea7'
REFERENCE_SHA='211c6b2f871fc5c2d9aa6c9a4f9b0a2c25fe2273a7dedb7ad9da2d689a6bdf93'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--campaign-root',required=True,type=Path)
    parser.add_argument('--evidence-repo',required=True,type=Path)
    parser.add_argument('--comparison-helper',type=Path)
    parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args();root=args.campaign_root.resolve();repo=args.evidence_repo.resolve()
    helper=args.comparison_helper or root/'compare_campaign_outputs.py'
    reference=repo/'verification/scripts/compare_featurecounts.py'
    if digest(helper)!=HELPER_SHA or digest(reference)!=REFERENCE_SHA:
        raise ValueError('Reviewed comparator source hash differs')
    spec=importlib.util.spec_from_file_location('historical_comparator',helper)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    ref=module.reference(reference)
    paths={
        'historical_dev_19f44e':('evidence-repository','verification/counts/dev/consensus_peaks.mLb.clN.featureCounts.txt'),
        'historical_pr448_5caa50':('evidence-repository','verification/counts/pr448/consensus_peaks.mLb.clN.featureCounts.tsv'),
        'new_unfixed_73155d':('campaign','outputs/pr448-hiv-bwa-unfixed-a9b588/bwa/merged_library/macs3/broad_peak/consensus/consensus_peaks.mLb.clN.featureCounts.tsv'),
        'new_fixed_a9b588':('campaign','outputs/pr448-hiv-bwa-fixed-a9b588/bwa/merged_library/macs3/broad_peak/consensus/consensus_peaks.mLb.clN.featureCounts.tsv'),
    }
    actual={k:(repo if scope=='evidence-repository' else root)/path for k,(scope,path) in paths.items()}
    report={'observed_at':datetime.now(timezone.utc).isoformat(),'schema':'pr448/historical-hiv-count-comparison/v1',
        'scope':'Archived historical HIV BWA library-consensus matrices versus fresh full-input runs. Historical FASTQ byte identity is not established; the archived dev source is not a fresh run of the immediate pre-448 parent.',
        'artifacts':{k:{'scope':scope,'path':path,'bytes':actual[k].stat().st_size,'sha256':digest(actual[k])} for k,(scope,path) in paths.items()},
        'comparators':{'helper_sha256':digest(helper),'reference_sha256':digest(reference),'script_sha256':digest(Path(__file__))},'pairs':{}}
    for left,right in [('historical_dev_19f44e','new_fixed_a9b588'),('historical_pr448_5caa50','new_unfixed_73155d'),('historical_dev_19f44e','new_unfixed_73155d')]:
        result=module.compare_counts(actual[left],actual[right],ref)
        report['pairs'][left+'_vs_'+right]=result
        print(json.dumps({'comparison':left+'_vs_'+right,'equal_counts_and_coordinates':result['equal_counts_and_coordinates'],
            'changed_cells':len(result['changed_cells']),'only_left':len(result['only_unfixed_rows']),'only_right':len(result['only_fixed_rows'])}))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')

if __name__=='__main__':main()
