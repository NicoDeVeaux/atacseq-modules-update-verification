# nf-core module history after the revisions installed by PR #448

Pinned upstream master: `a582d5` (2026-10-28). Pipeline comparison: base `4177ea` to merge `a51bee`. Each range starts at that module’s exact post-merge `modules.json` SHA, not a shared date or the pipeline merge commit.

Coverage: **36 changed module paths: 35 retained, one removed**. All 35 installed revisions are ancestors of the pinned master. The independent inventory matches every path and installed SHA. There are **78 module/commit associations across 21 distinct later commits**. The table below covers all 36 paths.

These are source-history conclusions. No new atacseq execution defect is claimed without a reproduction. Several upstream corrections were already merged before PR #448 itself merged on 2026-09-29. “Later” here means later than the installed module revision.

## Corrections worth considering, with applicability limits

| Component | Primary upstream change | Diff-confirmed change | Atacseq qualification |
|---|---|---|---|
| Trim Galore | [#12978](https://github.com/nf-core/modules/pull/12978), [e0dce2](https://github.com/nf-core/modules/commit/e0dce27411e04123f0fee60eb0f475262c165766) | Removes the 1 GB resource label implicated in cgroup/page-cache OOMs. | No `process_low_memory` selector in shipped atacseq; `process_medium` requests 36 GB. Not a demonstrated fault here. |
| Trim Galore | [#12986](https://github.com/nf-core/modules/pull/12986), [f97696](https://github.com/nf-core/modules/commit/f97696ae2ba28e94032adafea6777d7eb38d2c1d) | Captures optional JSON trimming reports for modern MultiQC. | Pipeline imports local MultiQC **1.13**, not its updated nf-core MultiQC module. Text-log/cutadapt plots exist in saved reports. Plan caller/report wiring when migrating MultiQC; no current missing-section claim. |
| GFFREAD | [#13024](https://github.com/nf-core/modules/pull/13024), [b3d1ca](https://github.com/nf-core/modules/commit/b3d1ca84b3f0051498abb91bd4333b701be4384d) | Decompresses gzip GFF/FASTA inputs; avoids silent empty GFF output. | `PREPARE_GENOME` already decompresses `.gff.gz` and passes no FASTA to GFFREAD. The direct-gzip failure path is bypassed. |
| ATAQV / mkarv | [#12112](https://github.com/nf-core/modules/pull/12112), [5909fc](https://github.com/nf-core/modules/commit/5909fc046b4b2062e4b4173808aacd2424e0866a) | Captures version-query stderr/non-zero behaviour directly instead of echo/command substitution. | Software-version provenance correction; processing commands unchanged. |

Other runtime changes are not automatically bug fixes. [PRESEQ #12612](https://github.com/nf-core/modules/pull/12612) changes the version-extraction expression and equivalent interpolation, without changing `lc_extrap` options. [DeepTools #13082](https://github.com/nf-core/modules/pull/13082) adds blacklist input and changes the BED tuple signature, so a full module sync needs caller changes. [Picard #12753](https://github.com/nf-core/modules/pull/12753) bumps 3.4.0→3.5.0 and removes `ext.suffix` handling in two wrappers; atacseq sets no such override.

The explicit fix-labelled changes [#12581](https://github.com/nf-core/modules/pull/12581) and [#12882](https://github.com/nf-core/modules/pull/12882) only repair links/output documentation for the audited components. Container commits closing [#13256](https://github.com/nf-core/modules/issues/13256) and [#13237](https://github.com/nf-core/modules/issues/13237) implement migration tasks, without changing processing commands.

## Complete module coverage

“Files” counts later commits touching `main.nf`, `environment.yml`, or lock files; it includes version/container/licensing changes and does not mean computational fixes.

| Module | Installed SHA | Later commits | Runtime-file touches | Later change categories |
|---|---|---:|---:|---|
| ataqv/ataqv | `6d4678` | 2 | 2 | licensing-only, module-provenance-fix |
| ataqv/mkarv | `6d4678` | 2 | 2 | licensing-only, module-provenance-fix |
| bowtie2/align | `a0961c` | 4 | 2 | licensing-only, metadata-formatting-only, tests-only, tool-version-bump |
| bowtie2/build | `a0961c` | 2 | 2 | licensing-only, tool-version-bump |
| bwa/index | `6d4678` | 1 | 1 | licensing-only |
| bwa/mem | `2fb127` | 1 | 1 | licensing-only |
| chromap/chromap | `f2f969` | 1 | 1 | licensing-only |
| chromap/index | `f2f969` | 1 | 1 | licensing-only |
| custom/getchromsizes | removed | — | — | Replaced by samtools/faidx; not installed after #448. |
| deeptools/alignmentsieve | `6d4678` | 3 | 2 | container-maintenance, documentation-only, licensing-only |
| deeptools/computematrix | `6d4678` | 3 | 3 | container-maintenance, licensing-only, module-feature-and-input-api-change |
| deeptools/plotfingerprint | `6d4678` | 2 | 2 | container-maintenance, licensing-only |
| deeptools/plotheatmap | `6d4678` | 2 | 2 | container-maintenance, licensing-only |
| deeptools/plotprofile | `6d4678` | 2 | 2 | container-maintenance, licensing-only |
| gffread | `c9ad4d` | 2 | 2 | licensing-only, module-compressed-input-fix |
| gunzip | `0902ea` | 1 | 1 | licensing-only |
| homer/annotatepeaks | `9ed7f1` | 1 | 1 | licensing-only |
| khmer/uniquekmers | `995d1b` | 1 | 1 | licensing-only |
| macs3/callpeak | `6d4678` | 2 | 1 | documentation-only, licensing-only |
| multiqc | `98403d` | 1 | 1 | licensing-only |
| picard/addorreplacereadgroups | `6d4678` | 3 | 3 | container-and-lock-maintenance, licensing-only, tool-version-bump-and-api-cleanup |
| picard/collectmultiplemetrics | `6d4678` | 3 | 3 | container-and-lock-maintenance, licensing-only, tool-version-bump-and-api-cleanup |
| picard/markduplicates | `6d4678` | 3 | 3 | container-and-lock-maintenance, licensing-only, tool-version-bump-and-api-cleanup |
| picard/mergesamfiles | `6d4678` | 3 | 3 | container-and-lock-maintenance, licensing-only, tool-version-bump-and-api-cleanup |
| preseq/lcextrap | `6d4678` | 2 | 2 | licensing-only, version-provenance-cleanup |
| samtools/faidx | `6d4678` | 4 | 4 | container-and-lock-maintenance, licensing-only, tool-version-bump |
| samtools/flagstat | `933980` | 3 | 3 | container-and-lock-maintenance, licensing-only, tool-version-bump |
| samtools/idxstats | `933980` | 3 | 3 | container-and-lock-maintenance, licensing-only, tool-version-bump |
| samtools/index | `933980` | 3 | 3 | container-and-lock-maintenance, licensing-only, tool-version-bump |
| samtools/sort | `933980` | 3 | 3 | container-and-lock-maintenance, licensing-only, tool-version-bump |
| samtools/stats | `933980` | 3 | 3 | container-and-lock-maintenance, licensing-only, tool-version-bump |
| subread/featurecounts | `6d4678` | 2 | 1 | documentation-only, licensing-only |
| trimgalore | `0991b1` | 4 | 4 | licensing-only, module-output-propagation-fix, module-resource-compatibility-fix, tool-version-bump |
| ucsc/bedgraphtobigwig | `6d4678` | 2 | 2 | container-maintenance, licensing-only |
| umitools/extract | `6d4678` | 2 | 1 | licensing-only, tests-only |
| untar | `6d4678` | 1 | 1 | licensing-only |

## All distinct subsequent commits

Every commit below has its affected component paths and classification in `nfcore-history.json`. Relevant diffs were inspected; titles were not treated as evidence of runtime defects.

| Date | Commit / PR | Classification |
|---|---|---|
| 2026-06-23 | [5909fc](https://github.com/nf-core/modules/commit/5909fc046b4b2062e4b4173808aacd2424e0866a) / [12112](https://github.com/nf-core/modules/pull/12112) | module-provenance-fix |
| 2026-07-09 | [2a30bf](https://github.com/nf-core/modules/commit/2a30bfb6a1b4667692d734e33e000a3bd1d74a0d) / [12331](https://github.com/nf-core/modules/pull/12331) | tool-version-bump |
| 2026-07-13 | [933980](https://github.com/nf-core/modules/commit/9339809fcb90af8a8b7051e6cd914894d5c52002) / [12340](https://github.com/nf-core/modules/pull/12340) | tool-version-bump |
| 2026-07-15 | [0cd85f](https://github.com/nf-core/modules/commit/0cd85f32cf1a1828205b16e4267277ba9457570b) / [12348](https://github.com/nf-core/modules/pull/12348) | tests-only |
| 2026-07-28 | [208039](https://github.com/nf-core/modules/commit/2080397432fcb0d079121dbacf22ce42ef175cec) / [12403](https://github.com/nf-core/modules/pull/12403) | metadata-formatting-only |
| 2026-08-10 | [85c172](https://github.com/nf-core/modules/commit/85c1724990b626767f9ed59092430d2d145c4607) / [12612](https://github.com/nf-core/modules/pull/12612) | version-provenance-cleanup |
| 2026-08-15 | [c565f1](https://github.com/nf-core/modules/commit/c565f1b27c06a1e8b726e2a646d4c822ae3b514a) / [12581](https://github.com/nf-core/modules/pull/12581) | documentation-only |
| 2026-08-20 | [fe0812](https://github.com/nf-core/modules/commit/fe08122c3dc2f2d7890daba06f6c90e570ef01de) / [12753](https://github.com/nf-core/modules/pull/12753) | tool-version-bump-and-api-cleanup |
| 2026-08-26 | [4dd270](https://github.com/nf-core/modules/commit/4dd270e412e2a7e78761be38aafa5cfa1dcdf891) / [12790](https://github.com/nf-core/modules/pull/12790) | tests-only |
| 2026-09-04 | [6ef220](https://github.com/nf-core/modules/commit/6ef220fd9252b42fb3c50348bbdbcb6246730686) / [12882](https://github.com/nf-core/modules/pull/12882) | documentation-only |
| 2026-09-16 | [e0dce2](https://github.com/nf-core/modules/commit/e0dce27411e04123f0fee60eb0f475262c165766) / [12978](https://github.com/nf-core/modules/pull/12978) | module-resource-compatibility-fix |
| 2026-09-17 | [f97696](https://github.com/nf-core/modules/commit/f97696ae2ba28e94032adafea6777d7eb38d2c1d) / [12986](https://github.com/nf-core/modules/pull/12986) | module-output-propagation-fix |
| 2026-09-24 | [b3d1ca](https://github.com/nf-core/modules/commit/b3d1ca84b3f0051498abb91bd4333b701be4384d) / [13024](https://github.com/nf-core/modules/pull/13024) | module-compressed-input-fix |
| 2026-10-04 | [50023b](https://github.com/nf-core/modules/commit/50023bebcce2b70e17a4759add65fac5781bfa4f) / [13082](https://github.com/nf-core/modules/pull/13082) | module-feature-and-input-api-change |
| 2026-10-15 | [b034b6](https://github.com/nf-core/modules/commit/b034b63f3160144d052de6f38350339a32f91489) / [13242](https://github.com/nf-core/modules/pull/13242) | container-maintenance |
| 2026-10-16 | [e848c6](https://github.com/nf-core/modules/commit/e848c6b4ae9cef4ac56d7221278185ebb31fe322) / [13257](https://github.com/nf-core/modules/pull/13257) | container-maintenance |
| 2026-10-19 | [5f344f](https://github.com/nf-core/modules/commit/5f344f0e41fdfaf2506f89400e42a2689d6ab323) / [13382](https://github.com/nf-core/modules/pull/13382) | container-and-lock-maintenance |
| 2026-10-20 | [467c84](https://github.com/nf-core/modules/commit/467c847035812fc17db844c6f37615b415b75eb3) / [13410](https://github.com/nf-core/modules/pull/13410) | container-and-lock-maintenance |
| 2026-10-20 | [8278e3](https://github.com/nf-core/modules/commit/8278e3c8a48427f7c26754128eba4907b8318878) / [13417](https://github.com/nf-core/modules/pull/13417) | tool-version-bump |
| 2026-10-27 | [7b3452](https://github.com/nf-core/modules/commit/7b3452a23773f687ededb4befd037920e5a51341) / [13448](https://github.com/nf-core/modules/pull/13448) | licensing-only |
| 2026-10-28 | [a582d5](https://github.com/nf-core/modules/commit/a582d5633f7df32396681ef4458068e2b509ca91) / [13473](https://github.com/nf-core/modules/pull/13473) | tool-version-bump |

## Verification and boundaries

A byte-for-byte suffix check confirms that the common licensing commit only prepends its header to all 35 retained module bodies. Another 26 component/commit checks confirm that the inspected packaging/version commits change only the container directive within `main.nf`; associated environment version changes remain explicitly classified. Machine-readable checks are in `nfcore-inspection-checks.json`.

Actual merged `main.nf` bytes match the declared upstream installed source for **33 of 35** retained modules. The exceptions are the intentional local BWA index resource patch and the Subread featureCounts **2.0.1** pin/patch. Preserve those deviations when evaluating an update; replacing them with the unpatched upstream source is not an innocuous refresh.

This module-only track excludes the seven separately inventoried shared subworkflows, underlying tool release notes, dependency-level fixes inside changed image builds, and unmerged upstream PRs. It did not modify source or launch workflows. `inventory.json` supplies the exact runtime/tool pins; this history audit does not infer opaque image contents.


The seven shared subworkflow histories have now also been audited separately: [nfcore-subworkflow-history.md](nfcore-subworkflow-history.md). Combined coverage is 43 changed shared components, including the removed module.
