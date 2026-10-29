# PR448: later upstream bug fixes

Completed 28 October 2026 against pinned source history and primary upstream releases. The inventory accounts for **all 267 changed module/subworkflow files**, covering **70 components**. Every one of the **16 declared dependencies whose versions changed** has a corresponding upstream scan below. The shared nf-core history check covers **36 module paths and all 7 shared subworkflows**, classifying **22 distinct later upstream commits**.

The comparison is the actual PR448 merge `a51bee` against its first parent `4177ea`. “Later” means after the selected tool/module revision; some fixes were already available before the pipeline PR merged. Declared versions and container references are recorded separately. Opaque image contents were not inferred, and this is not an exhaustive transitive-package or issue-tracker audit.

## What matters most

- **Trim Galore:** the known wrong-end R2 clipping correction is in 2.3.0. The frozen proposal `a9b588` already combines it with `--no_poly_g` to preserve the pipeline's earlier default. This issue has actual reproductions; the new candidates below have not been reproduced as additional pipeline regressions. [Upstream fix](https://github.com/FelixKrueger/TrimGalore/pull/322).
- **SAMtools statistics:** later [1.25 / #2388](https://github.com/samtools/samtools/pull/2388) corrects duplicate and insert-size QC statistics for specific record flags/zero insert lengths. The pipeline uses `samtools stats`, making this worth a targeted trigger test. This does not establish changes in flagstat, normalization, peaks or counts.
- **Picard:** [3.5.0 / #2034](https://github.com/broadinstitute/picard/pull/2034) repairs physical-coordinate overflow in optical-duplicate handling on large flowcells. The pipeline uses MarkDuplicates, but triggering read names and actual output impact require checking.
- **deepTools:** [4.0.0](https://github.com/deeptools/deepTools/releases/tag/4.0.0) includes matrix-boundary changes relevant to the pipeline's `--missingDataAsZero`. It is also a substantial backend/numerical rewrite, so it requires its own comparison rather than a blind version bump.
- **GFFREAD:** [0.12.9](https://github.com/gpertea/gffread/releases/tag/v0.12.9) repairs large-GFF-field parsing. The optional GFF-to-GTF path can use that parser; the HIV runs supply GTF, so they do not exercise that trigger.
- **Existing debt:** [Subread 2.0.4](https://subread.sourceforge.net/) repairs overlap-fraction precision; the retained 2.0.1 pin is used with `--fracOverlap 0.2`. It predates PR448 and must be considered alongside the deliberate paired-counting pin. Actual reporting still uses **local MultiQC 1.13**, so upgrading the unused nf-core MultiQC entry to 1.35 did not deliver its later parser fixes.

## Every declared dependency version change

| Dependency | PR448-selected version(s) | Later upstream scan and conclusion |
|---|---|---|
| Bowtie2 | 2.5.4 | 2.5.5 checked; no ordinary alignment/index correctness fix identified in its release notes. |
| BWA | 0.7.19 | Latest release unchanged; four post-tag default-branch commits affect README/CI, not executable alignment. |
| Chromap | 0.3.2 | Latest release unchanged; later barcode-summary/pairs-output work is outside the bulk SAM mode used here. |
| deepTools | 3.5.6 | 4.0.0 matrix/blacklist/order fixes reviewed, with major-rewrite and option qualifications. |
| GFFREAD | 0.12.7 | 0.12.9 large-field parser correction; conditional GFF-input relevance. |
| GNU grep | 3.11 | 3.12 corrections reviewed; inspected wrappers do not use the affected recursive/match-limit forms. |
| HTSlib | 1.22.1 / 1.24, plus other bundled pins | 1.24.1/1.25 and maintenance notes checked; format/error-path robustness exists, but exact linked build and trigger matter. |
| MACS3 | 3.0.4 | 3.0.5/3.1.0 checked. Important summit/duplicate/Poisson fixes have option/reachability exclusions; BAM validation/worker robustness remains relevant. |
| MultiQC | unused nf-core entry 1.35 | Actual workflow uses local 1.13. Parser follow-ups concern existing reporting debt, not a delivered 1.35 runtime. |
| Picard | 3.4.0 | 3.5.0 optical-coordinate correction; flow-specific fixes are outside normal Illumina options. |
| pigz | 2.8 | Default-branch head equals the tag: no later merged correction in that range. |
| preseq | 3.2.0 | Latest stable unchanged; substantial unreleased rewrite inspected without attributing its new-code fixes to the pinned release. |
| SAMtools | 1.21 / 1.22.1 / 1.23.1 / 1.24 | 1.25 QC-statistics and maintenance robustness fixes checked. |
| GNU sed | 4.8 | 4.9 fixes reviewed; no documented trigger identified in the simple ASCII version substitutions used here. |
| Trim Galore | 2.1.0 | Reproduced R2 correction in 2.3.0; included in the separately frozen proposal. |
| UCSC bedGraphToBigWig | 482 | Later merged compressed-input rewind fix checked; this pipeline supplies sorted uncompressed bedGraph. |

Primary links, exact refs/dates, command/config evidence and exclusions for each row are in [alignment/QC software](software-alignment-qc.md), [preprocessing/reporting software](software-preprocessing.md), and [system tools](software-system-tools.md). `coverage.json` maps every changed dependency back to the affected component paths and its report.

## Shared wrapper and subworkflow fixes

The complete [module-history report](nfcore-history.md) and [seven-subworkflow report](nfcore-subworkflow-history.md) distinguish processing changes from licensing, tests, containers and version provenance.

The later Trim Galore resource-label and JSON-report corrections are real upstream changes, but applicability needs care: atacseq has no low-memory label selector, requests 36 GB through its medium label, and still consumes trimming text reports through local MultiQC 1.13. The GFFREAD gzip-wrapper issue is bypassed because genome preparation already decompresses GFF input. ATAQV's version capture is a provenance correction. The subworkflow JSON emit needs coordinated caller/report wiring when modernizing reporting.

Intentional local changes in BWA indexing and the Subread 2.0.1 wrapper were identified. They must survive any future module sync. No later queue/value, library-metadata or version-topic logic correction was found in the seven checked subworkflow histories.

## Reproducibility and current work

- [Inventory](inventory.tsv) / `inventory.json`: exact old/new dependency and image declarations, source hashes, installed module SHAs, changed files and static reachability.
- [Coverage](coverage.json): 16 dependency changes accounted for, 43 shared component histories and evidence checksums.
- Individual JSON reports retain primary release/commit/PR references and explicit limitations.
- The four full HIV comparisons are a separate, ongoing campaign described in `../original-cohorts/RERUN_PLAN.md`. Their published proposal remains frozen at `a9b588`; this audit has not changed any run's source or versions. Platform permits three active workflows, so the fourth arm waits for a slot.

A truthful concise summary is: “For extra confidence, I checked every declared version change in #448 against subsequent upstream releases and merged module fixes, reviewed applicability to this pipeline, and documented the follow-up candidates alongside the real-data comparison.” This describes the completed scan; it does not claim every upstream fix is relevant or that untested candidates are new pipeline findings.
