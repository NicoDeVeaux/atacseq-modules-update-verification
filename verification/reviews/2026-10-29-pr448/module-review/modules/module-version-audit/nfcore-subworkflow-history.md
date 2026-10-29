# Shared nf-core subworkflow history after PR #448 installed revisions

All **seven** changed shared subworkflows were inspected from their exact post-merge `modules.json` SHA to upstream master `a582d5`. All seven installed `main.nf` files match the declared upstream bytes; all installed commits are ancestors of the pinned master.

Coverage totals: **23 subworkflow/commit associations across seven distinct commits**. Together with the module-only audit, this covers **43 changed shared components (42 retained, one removed)** and **22 distinct subsequent commits**.

## Runtime conclusion

The only non-licensing `main.nf` change in these seven histories is [ea400d](https://github.com/nf-core/modules/commit/ea400d55ea0a63c1a0f9fd527211208b842ea15e), [PR #12998](https://github.com/nf-core/modules/pull/12998), merged 2026-09-19. It forwards the new Trim Galore JSON report through `ch_trim_json` and a `trim_json` emit. The underlying module output was added by [PR #12986](https://github.com/nf-core/modules/pull/12986). Module and subworkflow updates need to stay together; an eventual MultiQC consumer also needs to collect the new emit.

This is an output-propagation correction, not a change to read filtering, library metadata, queue/value pairing, alignment, or version-topic wiring. It was already upstream before pipeline PR #448 merged. Atacseq uses a local **MultiQC 1.13** wrapper with text-log/cutadapt plots in the saved reports, so this audit does not claim that the current pipeline loses its trimming section. It identifies the required interface when moving to modern MultiQC.

Every other later `main.nf` change is the common copyright/licence header. Removing that prefix restores the previous file byte-for-byte for all seven. Fix-labelled [PR #12882](https://github.com/nf-core/modules/pull/12882) only updates `meta.yml` to describe the already-existing channel interfaces. The remaining commits touch tests/snapshots only within these subworkflow paths.

## Complete coverage

| Shared subworkflow | Installed SHA | Later commits | Main-file touches | Non-licensing runtime change |
|---|---|---:|---:|---|
| bam_markduplicates_picard | `933980` | 4 | 1 | None |
| bam_sort_stats_samtools | `933980` | 4 | 1 | None |
| bam_stats_samtools | `933980` | 4 | 1 | None |
| fastq_align_bowtie2 | `a0961c` | 3 | 1 | None |
| fastq_align_bwa | `cbb7a6` | 2 | 1 | None |
| fastq_align_chromap | `d92e0f` | 3 | 1 | None |
| fastq_fastqc_umitools_trimgalore | `e5777e` | 3 | 2 | Trim Galore JSON report propagation |

## All distinct subsequent commits

| Date | Commit / PR | Classification within the audited subworkflows |
|---|---|---|
| 2026-07-15 | [0cd85f](https://github.com/nf-core/modules/commit/0cd85f32cf1a1828205b16e4267277ba9457570b) / [12348](https://github.com/nf-core/modules/pull/12348) | tests-only |
| 2026-08-20 | [fe0812](https://github.com/nf-core/modules/commit/fe08122c3dc2f2d7890daba06f6c90e570ef01de) / [12753](https://github.com/nf-core/modules/pull/12753) | tests-only |
| 2026-09-04 | [6ef220](https://github.com/nf-core/modules/commit/6ef220fd9252b42fb3c50348bbdbcb6246730686) / [12882](https://github.com/nf-core/modules/pull/12882) | documentation-only |
| 2026-09-19 | [ea400d](https://github.com/nf-core/modules/commit/ea400d55ea0a63c1a0f9fd527211208b842ea15e) / [12998](https://github.com/nf-core/modules/pull/12998) | output-propagation-fix |
| 2026-10-19 | [5f344f](https://github.com/nf-core/modules/commit/5f344f0e41fdfaf2506f89400e42a2689d6ab323) / [13382](https://github.com/nf-core/modules/pull/13382) | tests-only |
| 2026-10-27 | [7b3452](https://github.com/nf-core/modules/commit/7b3452a23773f687ededb4befd037920e5a51341) / [13448](https://github.com/nf-core/modules/pull/13448) | licensing-only |
| 2026-10-28 | [a582d5](https://github.com/nf-core/modules/commit/a582d5633f7df32396681ef4458068e2b509ca91) / [13473](https://github.com/nf-core/modules/pull/13473) | tests-only |

The machine-readable report records every changed path, exact installed SHA, subsequent commit, and classification. `nfcore-history.json` / `.md` contain the companion module audit. No source changes or runtime/cloud actions were performed for this extension.
