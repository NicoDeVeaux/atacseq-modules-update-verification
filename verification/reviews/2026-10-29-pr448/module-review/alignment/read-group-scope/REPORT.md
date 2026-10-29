# Read-group scope clarification: inherited BWA/Bowtie2 versus PR448 Chromap

**BWA and Bowtie2 already used the technical-run ID as the library ID before PR448, and those read-group arguments are active on the normal default input path.** This is inherited configuration, distinct from PR448 introducing a read-group replacement step for Chromap. STAR is different: its explicit read-group arguments contain ID/SM but no LB. This source clarification establishes configuration/history; it does not establish a new deduplication finding or quantify its scientific effect.

Reviewed exact source commits: parent `4177ea`, PR448 merge `a51bee`, and current review checkout `73155d`. Full commits, Git blob IDs and SHA256 hashes for the 33 preserved files are in `pins.json`. The previous 181-file alignment/peak lane was left untouched.

## Technical-run IDs are generated before all aligners

`bin/check_samplesheet.py:208–214` writes each input run as `sample_REP{replicate}_T{idx+1}`. This file is byte-identical at all three commits. Thus two FASTQ rows for the same sample/replicate receive, for example, `D28P_REP1_T1` and `D28P_REP1_T2`. Even a single row receives `_T1`.

The parent `subworkflows/local/input_check.nf:29–37` assigns that normalized `row.sample` to `meta.id` and always constructs:

```text
ID:meta.id  SM:meta.id minus terminal _T<number>  PL:ILLUMINA  LB:meta.id  PU:1
```

An optional sequencing center adds CN; it does not enable/disable read groups. The same construction remains at merge/current `input_check.nf:26–34`.

## Per-aligner source result

| Aligner | Parent 4177ea | Merge/current | Normal input-path activation |
| --- | --- | --- | --- |
| BWA | `-R ${meta.read_group}`, whose LB includes `_Tn` | Same LB construction/argument | `meta.read_group` is always nonempty after input checking; BWA is the default aligner |
| Bowtie2 | `--rg-id ${meta.id}` and `--rg LB:${meta.id}`; SM strips `_Tn` | Same LB construction/argument | The guard is `meta.read_group`, which is always nonempty on this path; active when Bowtie2 is selected |
| Chromap | No post-mapping Picard read-group step in `FASTQ_ALIGN_CHROMAP` | PR448 adds Picard AddOrReplaceReadGroups and `--RGLB ${meta.id}` | The main pipeline supplies `true` to the new add-read-groups input; active when Chromap is selected |
| STAR | `--outSAMattrRGline ID:$prefix 'SM:$prefix'`, optional CN; no explicit LB | Same ID/SM/no-LB construction | Always inserted by the local STAR module when STAR is selected; prefix defaults to `meta.id` |

Precise references:

- Both parent and merge/current `conf/modules.config:225–233`: BWA's read-group guard/argument. The BWA module interpolates `task.ext.args` into `bwa mem`; this is not unused configuration.
- Both parent and merge/current `conf/modules.config:245–251`: Bowtie2 read-group guard and technical-run LB. The optional CN quoting differs in PR448; the LB expression does not. The Bowtie2 module interpolates these arguments into the actual mapper command.
- Parent `input_check.nf:33–37` versus merge/current `:30–34`: BWA's actual LB content and the guard's nonempty source.
- Both parent and merge/current `nextflow.config:13` sets `seq_center=null`, while `:38` sets `aligner='bwa'`. A null sequencing center leaves the non-CN read-group string present. There is no separate opt-in read-group parameter in this normal path.
- Merge/current `conf/modules.config:297–307`: Chromap Picard RGID retains `_Tn`, RGSM strips it, RGLB retains it. Parent has no corresponding selector or Picard module call in its Chromap subworkflow.
- Parent `modules/local/star_align.nf:33–35`, merge/current `:32–34`: prefix and STAR's ID/SM-only arguments. Do not describe STAR as explicitly emitting the same per-run LB pattern.

After alignment the parent workflow removes `meta.read_group`, strips `_Tn` from channel `meta.id`, groups the technical runs, then calls `PICARD_MERGESAMFILES_LIBRARY` and merged-library MarkDuplicates (`workflows/atacseq.nf:251–284`; merge/current `:239–272`). These channel metadata operations do not themselves issue a BAM read-group/library rewrite. This explains why stripping `_Tn` from channel identity is not evidence that the earlier BWA/Bowtie2 LB value was shared between runs.

## Suggested upstream scope wording

> This fixes the Chromap resequencing regression introduced by PR448's new per-run read-group replacement step. BWA and Bowtie2 already used technical-run library IDs before PR448; changing their library semantics would be a separate behavioral change. The present fix does not establish that every aligner has identical read-group or cross-run duplicate-marking semantics.

If rows with the same sample/replicate are intended to represent resequencing of one physical library, BWA/Bowtie2's inherited per-run LB pattern deserves a separate, explicitly scoped duplicate-marking reproduction and samplesheet-semantics check. This audit did not run one and does not label that candidate as a newly confirmed bug. Custom process configuration can override the arguments described here.

No scientific jobs, cloud/model calls, pipeline edits, commits or publication were performed for this clarification.
