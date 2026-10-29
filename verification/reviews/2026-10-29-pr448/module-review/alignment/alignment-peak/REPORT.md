# PR448: reachable alignment and peak-call behavior changes

This bounded audit supports a focused TrimGalore/Chromap-read-group fix, but does **not** establish that all PR448 outputs should be identical to the parent. Chromap mapping, Bowtie2 reporting, BWA SAM metadata and MACS3 peak-file formatting demonstrably change across the versions selected by PR448. The controls below separate these changes from the two proposed pipeline fixes.

Scope: nf-core/atacseq parent `4177ea` versus merge `a51bee`; exact commits, module revisions, environment declarations, containers and source blobs are recorded in `pipeline/`. Primary upstream snapshots are in `primary/`; source-file snapshots have verified Git blob hashes. All new scientific controls used local Docker/Colima with container networking disabled and public real yeast reads/reference. No cloud jobs, model calls, source mutations or upstream publication were performed. These are direct tool controls using the pipeline's scientific arguments, rather than additional complete Nextflow runs.

## Actual versions and reachable arguments

| Component | Parent → PR448 | Reachable pipeline behavior |
| --- | --- | --- |
| BWA mem | 0.7.17 → 0.7.19 | `-M`; optional `-T` is absent by default (`bwa_min_score=null`); read group; paired FASTQ; subsequent samtools `-F 0x0100` |
| BWA index | 0.7.19 → 0.7.19 | Parent already used the newer index tool; this was not a 0.7.17→0.7.19 indexing upgrade |
| Bowtie2 align | 2.5.2 → 2.5.4 | Default paired mapping; read-group fields; no new `--sam-opt-config`, `-a` or `-k` override |
| Bowtie2 build | 2.4.4 → 2.5.4 | Reference index generation; index and mapper versions must be considered separately |
| Chromap index/map | 0.2.4 → 0.3.2 | `-l 2000 --low-mem --SAM`; optional `--Tn5-shift`; no barcode, summary, preset or internal duplicate removal flags |
| MACS3 callpeak | 3.0.1 → 3.0.4 | BAM/BAMPE, `--keep-dup all --nomodel`; broad peaks by default, optional narrow/control/bedGraph/p- or q-value settings |

Pinned configuration: merge `conf/modules.config:225` (BWA), `:245` (Bowtie2), `:279` (Chromap), `:627` and `:871` (library/replicate MACS3); `nextflow.config:39`. Both versions' whole focused files are preserved, not reconstructed from release-note version guesses.

## Chromap: an upstream mapping correction really changes aligned pairs

[Chromap 0.3.2](https://github.com/haowenz/chromap/releases/tag/v0.3.2) explicitly includes a best-pair selection fix. [Commit 6cde47](https://github.com/haowenz/chromap/commit/6cde47a1dc4c00b3e3a61fe6f7bcfbb0067bec89) changes which mate's length enters the paired-candidate upper bound. In `src/mapping_generator.h:441–448` at v0.3.2, positive-first mapping uses `read1_length` where the parent used `read2_length`, and the reverse branch uses `read2_length` where it previously used `read1_length`. This generic paired mapper is reachable in the pipeline's SAM mode.

The existing full-yeast comparison had one residual count-cell difference after the proposed fixes: 77→76 at chrIV:42072–43938 for D28P. The prior trace attributed the extra old cleaned pair to a duplicate decision after a newly available Chromap alignment. This audit independently isolates the **mapper difference**, using two actual pairs from that trace; their FASTQ records are identical in the parent and fixed trimming outputs. One has unequal mate lengths, 58/99 nt. With version-specific existing indexes, the pipeline's mapping arguments and the same sacCer3 FASTA:

| Actual read fixture | Chromap 0.2.4 SAM records | Chromap 0.3.2 SAM records |
| --- | ---: | ---: |
| Unequal-length pair alone | 0 | 2 |
| That pair plus the other affected actual pair | 2 | 4 |

The raw FASTQs, SAMs, commands and zero exit statuses are in `chromap-residual-pair/`. This rules out TrimGalore sequence differences as the explanation for this particular mapping discrepancy. It does **not** uniquely attribute the result to commit 6cde47: no single-commit rebuild/reversion was performed, and old/new indexes were not crossed in this small test. The release/source fix is a plausible mechanism, not a proven single-commit causal replay. Therefore complete parent/fix numerical equivalence is the wrong acceptance criterion.

A second control maps the same first 5,000 actual trimmed D28P pairs under both versions. Both produce 6,572 SAM records / 3,286 mapped QNAMEs, with identical multisets of all first 11 SAM fields. Exactly 92 records change only the MD tag, adding missing zero runs at adjacent mismatches or at boundaries (for example `88CA9`→`88C0A9`). NM, alignment positions/CIGAR/MAPQ and all other optional tags are identical in this control. The source change is visible in `chromap-range.json`, `src/alignment.cc`; this is a separate metadata correction, not extra mappings in this read prefix.

The 0.3.1 release's internal duplicate-removal changes are not evidence of a pipeline duplicate regression: `mapping_parameters.h:48` initializes `remove_pcr_duplicates=false`, and `chromap.h:1326` gates the corresponding branch. The pipeline does not enable it. Likewise the 0.3.0 FRiP/summary additions require summary/barcode modes not selected here. These exclusions do not cover every ordering/cache/thread interaction in the whole upstream delta.

## BWA: same alignment fields in a bounded control, expected extra SAM metadata

[BWA 0.7.19 release notes](https://github.com/lh3/bwa/releases/tag/v0.7.19) explicitly claim alignments identical to 0.7.17/0.7.18; this is an upstream claim, not a proof supplied by this audit. The range source adds an `@HD` header and an `MQ:i` mate-MAPQ tag by default (`bwamem.c:935` at the new range tip); optional XB handling is not enabled by the pipeline. ARM support and memory/thread portability changes also entered this range.

The same 5,000 real pairs, same BWA 0.7.19 index (matching the parent index version), `-M`, default score threshold and the same read group produce **10,003 SAM records in both versions**. Every first-11-field SAM record matches as a multiset. After the pipeline's `-F 0x0100` filter, both contain 10,000 records with identical alignment fields. Excluding the newly added MQ tag, all optional fields also match; MQ is added to all 10,003 records. Headers differ. See `bwa-bowtie-same-reads/comparison.json` and the saved SAMs. Do not require byte-identical BAM files across these tool versions.

This does not test human ALT/repetitive reference behavior, all supplementary alignment cases, single-end mode, explicit `bwa_min_score`, large batches, or native ARM versus amd64 execution. It provides no general proof that such modes are unchanged.

## Bowtie2: QC summary partition changes although the actual alignments match

[Bowtie2 2.5.4 notes](https://github.com/BenLangmead/bowtie2/releases/tag/v2.5.4) describe reverting a concordant-alignment counting change introduced in 2.5.0. The [actual fix 3e25cb](https://github.com/BenLangmead/bowtie2/commit/3e25cb9c8fe423b479275cee8e573b0cf13f3646) changes the `aln_sink.cpp` reporting-counter branch (`met.nconcord_uni1/uni2`), not SAM selection. The release wording says unique over-counting; the commit subject instead says repetitive over-counting. The code and actual controlled result establish the direction here, so the release shorthand should not be used to predict that direction.

The same 5,000 real pairs were aligned with both mapper versions against **both** 2.4.4 and 2.5.4 indexes (four combinations). All combinations emit exactly 10,000 SAM records and identical multisets of first 11 fields **and all optional fields**. The total alignment rate remains 96.33%. Yet the stderr concordant partition changes:

| Mapper | Exactly one concordant alignment | More than one concordant alignment |
| --- | ---: | ---: |
| 2.5.2 | 2,988 (59.76%) | 1,556 (31.12%) |
| 2.5.4 | 3,039 (60.78%) | 1,505 (30.10%) |

Thus MultiQC/QC summary differences can be real, expected upstream reporting corrections even with unchanged BAM alignments. This is an **introduced behavior change**, but the local evidence does not show a new mapper correctness regression. The previously released 2.5.1 accuracy fix was already in parent **align 2.5.2**; it must not be attributed to PR448 merely because its parent **builder** was older.

Other included changes concern empty FASTQ records, FASTA option parsing, BAM-input memory and partial writes; their relevance differs from the default valid paired FASTQ path. New SAM-tag toggles are opt-in and absent here. Optional libsais indexing has different small-index limits; the tiny yeast cross-index control does not establish human-sized index/resource compatibility or identify every compiled backend difference in the images.

## MACS3: peak-score controls agree, while gappedPeak formatting changes

[3.0.2](https://github.com/macs3-project/MACS/releases/tag/v3.0.2) changes compiler optimization (`-Ofast`→`-O3`) and peak-file formatting. [3.0.3](https://github.com/macs3-project/MACS/releases/tag/v3.0.3) includes a broad Cython source-style rewrite and NumPy2 support, plus FRAG/HMMRATAC changes. The latter modes are not the pipeline's BAM/BAMPE `callpeak` path.

Do **not** claim [3.0.4's NaN/overflow fix #717](https://github.com/macs3-project/MACS/pull/717) proves that PR448 fixes large-human callpeak q-values. Its patch changes `ScoreTrackII.compute_pvalue` in `Signal/ScoreTrack.py:409–437`. The actual `callpeak_cmd`→`PeakDetect` path instantiates `CallerFromAlignments` (`PeakDetect.py:234`, `:350`) from `CallPeakUnit`; the old v3.0.1 implementation already used 64-bit `N`, `k` and interval length there (`CallPeakUnit.pyx:623–629`). The source distinguishes these paths; no trigger on pipeline callpeak was demonstrated.

Six local calls compare 3.0.1/3.0.4 on **the identical actual D28P cleaned BAM**, holding alignment/filter/dedup upstream outputs fixed. Exact pipeline BAMPE/broad arguments yield 1,431 broad peaks; narrow mode yields 1,150 narrow peaks; broad mode with the actual D28 cleaned control yields one broad peak. For each old/new pair, every broadPeak/narrowPeak field and every non-comment XLS row is identical, including numerical scores/p-values/q-values. This is stronger than merely comparing peak counts, but remains a small yeast control; the one-peak control is particularly weak coverage of complex treatment/control behavior.

All gappedPeak rows change fields 7/8 to zero; every other field is identical in these controls. This is explicit writer behavior: old `IO/PeakIO.pyx:1100–1105` emits stored thickStart/thickEnd, new `IO/PeakIO.py:1383–1399` writes literal zero fields. It is consistent with the release's format-compatibility change (linked issue [#653](https://github.com/macs3-project/MACS/issues/653)); the exact gappedPeak edit was established from code and output, not inferred from the issue title. Whole XLS hashes also differ due to comments containing tool version/date. Neither difference establishes changed peak statistics.

## What remains before broader scientific confidence

The review has reproduced meaningful version differences and reduced specific risks; it has not closed all parameter/data coverage. Recommended minimal next discriminating controls, in priority order:

1. Keep the actual unequal-length Chromap pair as a permanent targeted regression witness. If exact causal attribution matters, rebuild old/new mapper around 6cde47 with one shared index and test the pipeline's SAM mode; separately test repeat/multimapping and Tn5-shift boundaries. Do not force the fixed full pipeline to reproduce an older missed alignment or its duplicate selection.
2. Compare old/new MACS3 on the **same human BAM(s)** using the real study's genome size, default broad and requested narrow modes, with/without control. Compare exact coordinates, numerical score columns and counts separately from version comments/gappedPeak display fields. Small yeast equality does not test billion-base accumulations or threshold-near-boundary floating behavior through the source/compiler changes. Add a bounded same-BAM SE mode if SE support is part of the upstream claim.
3. For BWA/Bowtie2, retain the read/index cross-controls and add a deliberately repetitive/ALT-rich public human read subset using the same reference/index. Verify primary/secondary/supplementary fields, MAPQ and downstream filtered counts; report Bowtie's corrected unique/multi QC partition separately. Use explicit score/preset/SE variants only when those are claimed supported/unchanged.
4. Use complete biological pipeline results to assess scientific agreement, with known intentional differences called out, rather than treating file hashes or total counts alone as correctness or equivalence proofs. These local mapper controls do not substitute for all remaining study/cohort/aligner comparisons.

No additional PR448-specific scientific defect in these four tools was established by this bounded task. That sentence is limited to the actual controls and focused source inspection above; it is not a blanket safety finding or a justification to say every upgraded module is behavior-preserving.

## Evidence and rerun

- `pipeline/`: parent/merge exact module/config files and full source/module pins.
- `primary/`: upstream releases, whole focused range comparisons, fix patches and Git-blob-verified source snapshots; all are public source, not credentials.
- `input-pins.json`, `container-pins.json`: reference/BAM/index and exact local container identities.
- `macs3-same-bam/`: 6 exact commands, outputs, logs, exit statuses and comparisons.
- `chromap-residual-pair/`: 4 exact commands, original two-pair fixtures, outputs and statuses.
- `chromap-5000-pairs/`: 2 commands, outputs, core and MD comparisons.
- `bwa-bowtie-same-reads/`: 3 index builds + 6 alignments, genuine selected reads/checksums, cross-index results and all SAMs/logs.
- `run_bwa_bowtie.py`: the local mapper harness. It requires the canonical real-samples tree; it overwrites only its own generated control outputs when explicitly rerun.
- `replay_command.py`: explicitly rerun one saved exact container command into a **new** output directory; original evidence stays intact. It uses cached images (`--pull=never`) and records the actual replay command.
- `check.py`: offline assertions on saved evidence and source snapshots; no scientific jobs or Docker execution.

Example offline verification: `python3 check.py`. Example isolated single-call replay: `python3 replay_command.py chromap-residual-pair/0.3.2/unequal_pair_only/command.json LOCAL_TMP`. Inputs/mounts still require this local canonical evidence tree. Full commands and pins make the scope reviewable; this staging directory is not a complete standalone reference/data distribution.
