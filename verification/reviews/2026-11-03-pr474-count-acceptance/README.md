# Issue 473: full BWA count acceptance replay

The [complete public count/SAF data package](../2026-11-03-count-saf-data/README.md) now includes the actual tables, both cell-delta witnesses, annotation files and boundary fixture, with original/distributed hashes and an offline verifier.

The original trimming repair reproduces **all 299,580 archived values**. The current PR with the SAF correction **does not meet the literal equality criterion**: 2,280 values change (0.761%), across 2,223 regions. No acceptance criterion or CI snapshot was changed for this replay.

| Sample | Archived sum | Corrected sum | Changed cells |
| --- | ---: | ---: | ---: |
| HIV_CD86HI_48H_REP1 | 755,472 | 755,031 | 438 |
| HIV_CD86HI_48H_REP2 | 1,049,186 | 1,048,552 | 630 |
| MOCK_48H_REP1 | 728,326 | 727,863 | 460 |
| MOCK_48H_REP2 | 1,207,245 | 1,206,490 | 752 |

Of 299,580 cells, 297,300 remain equal, 2,267 decrease by one and 13 decrease by two. No cells increase. The total decreases by 2,293 counts. Assignment-summary totals and regional-count sums differ because the original command permits overlapping features (`-O`).

## Controlled replay

- Candidate: [ef206a](https://github.com/NicoDeVeaux/atacseq-nfcore/commit/ef206a60f88b4c754eaf4d0a8c0b9ee0c9268180), [PR 474](https://github.com/nf-core/atacseq/pull/474), [issue 473](https://github.com/nf-core/atacseq/issues/473).
- Four preserved clean sorted BWA BAMs from workflow `BVYqNpYNcUhEN`, source [a9b588](https://github.com/NicoDeVeaux/atacseq-nfcore/commit/a9b588235e4a1ceb3c8838acad430628c5737c86). All 1,428,529,136 bytes were downloaded from the private preservation copy and independently SHA-256 checked against their recorded identities before execution.
- Original consensus BED, boolean input, SAF, fixed count table and actual task-140 command were retained unchanged. The archived dev matrix was read from the supporting-data repository and checked against its recorded SHA-256.
- First replay: original SAF, same BAMs and command. All 74,895 feature metadata records and all 299,580 named sample/feature values match both the historical fixed matrix and archived dev. The original dev sample columns use a different order; comparison checks the complete unique sample set and maps by exact BAM basename. The legacy assignment summary is byte-identical to the historical fixed summary.
- Intervention: execute the exact two-line SAF generator extracted from the current production module. Every start becomes BED start + 1; chromosome, end, feature ID, strand, row order and the complete feature set remain unchanged. Every corrected length is BED end minus BED start, one shorter than the legacy inclusive interval.
- Second replay: identical BAMs, image and original featureCounts flags/order, changing only the SAF. Every count cell and every row metadata field is checked; the complete delta table is retained privately. Per-sample total processed alignments are conserved. Only Assigned, Unassigned_NoFeatures and Unassigned_Overlapping_Length summary categories change.

The original counting command is:

```bash
featureCounts -F SAF -O --fracOverlap 0.2 -p -T 6 \
  -a consensus_peaks.mLb.clN.saf -s 0 \
  -o consensus_peaks.mLb.clN.featureCounts.tsv \
  HIV_CD86HI_48H_REP1.mLb.clN.sorted.bam \
  HIV_CD86HI_48H_REP2.mLb.clN.sorted.bam \
  MOCK_48H_REP1.mLb.clN.sorted.bam \
  MOCK_48H_REP2.mLb.clN.sorted.bam
```

An independently implemented comparator reproduces the same complete 2,280-cell delta set. Eleven parser controls pass, including rejection of a changed final cell, missing final row, missing/duplicate sample, duplicate feature ID, annotation mismatch and sample relabeling. Legacy zero-based starts remain visible to the audit rather than being filtered out.

## What this establishes

This isolates the numerical effect of the SAF correction on the full archived BWA cohort. The old-coordinate positive control establishes exact restoration by the trimming repair; the expanded PR intentionally uses different feature coordinates and fails the original count-value equality requirement. The coordinate conversion is checked across all regions. This is not an independent per-read oracle proving every new count correct.

No new alignment, peak calling, duplicate marking, normalization, or full workflow was run. Earlier resequencing/duplicate-marking evidence is unchanged and remains separately scoped; this recount does not re-qualify that behavior. The historical dev matrix is an archived dev result, not a new immediate-pre-448-parent run.

Both local counting arms use the same immutable official Subread 2.0.1 image. The original cloud image digest is unavailable, so this is a **local-image stage bridge**, supported by the complete legacy positive control, rather than an exact historical-image replay. Rosetta changes only the emitted command's executable spelling from `featureCounts` to `/usr/local/bin/featureCounts`; the complete arguments and all raw outputs are preserved.

Keeping the SAF correction in this PR requires an explicit review of this numerical impact and the equality criterion. No criterion was waived or rewritten, and the PR description was left unchanged.

This report was written by Codex on Nico DeVeaux's behalf; the exact runtime model identifier is unavailable.
