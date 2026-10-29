# Three-arm full-core output comparison

State: **COMPLETE_COMPARISON**. Observed: 2026-10-29T06:22:12.419999+00:00.

Full main.nf core analysis; optional deepTools/ATAQV/PRESEQ/DESeq2-QC/Picard CollectMultipleMetrics and R peak-QC plots off equally; two biological libraries, two technical runs each. No biological differential inference.

| Arm | Source | Completion | Artifact coverage | Missing required |
|---|---|---|---|---|
| base | 4177ea | True | True | none |
| unfixed | 73155d | True | True | none |
| fixed | a9b588 | True | True | none |


Recorded per-library values (QC-passed flagstat reads; `?` means unavailable):

| Arm / library | Marked primary mapped | Marked duplicates | Cleaned reads | Picard examined / duplicate pairs | Scale | FRiP | Broad peaks |
|---|---:|---:|---:|---:|---:|---:|---:|
| base / D28_REP1 | 645804 | 48210 | 564934 | 322902 / 24105 | 1.77012 | 0.350427 | 1635 |
| base / D28P_REP1 | 636394 | 39384 | 567510 | 318197 / 19692 | 1.76208 | 0.347007 | 1431 |
| unfixed / D28_REP1 | 645730 | 43000 | 569486 | 322865 / 21500 | 1.75597 | 0.322047 | 1406 |
| unfixed / D28P_REP1 | 636454 | 35594 | 570996 | 318227 / 17797 | 1.75133 | 0.350712 | 1436 |
| fixed / D28_REP1 | 645814 | 48210 | 564934 | 322907 / 24105 | 1.77012 | 0.350427 | 1635 |
| fixed / D28P_REP1 | 636404 | 39386 | 567508 | 318202 / 19693 | 1.76209 | 0.347005 | 1431 |

## base_vs_fixed

Matched artifacts: 24; unmatched/unreadable: 0.

| Artifact | Observed comparison |
|---|---|
| `chromap/merged_library/bigwig/scale/D28P_REP1.mLb.clN.scale_factor.txt` | 1 exact field differences |
| `chromap/merged_library/bigwig/scale/D28_REP1.mLb.clN.scale_factor.txt` | 0 exact field differences |
| `chromap/merged_library/macs3/broad_peak/D28P_REP1.mLb.clN_peaks.broadPeak` | intervals 1431 → 1431; exact Jaccard=1.0; bp Jaccard=1.0; peak value changes=2777 |
| `chromap/merged_library/macs3/broad_peak/D28_REP1.mLb.clN_peaks.broadPeak` | intervals 1635 → 1635; exact Jaccard=1.0; bp Jaccard=1.0; peak value changes=0 |
| `chromap/merged_library/macs3/broad_peak/consensus/consensus_peaks.mLb.clN.bed` | intervals 1934 → 1934; exact Jaccard=1.0; bp Jaccard=1.0; peak value changes=0 |
| `chromap/merged_library/macs3/broad_peak/consensus/consensus_peaks.mLb.clN.featureCounts.tsv` | counts equal=False; intervals 1934 → 1934; changed cells=1; versions v2.0.1 → v2.0.1; D28P_REP1: total 121568 → 121567, changed shared intervals 1; D28_REP1: total 119315 → 119315, changed shared intervals 0 |
| `chromap/merged_library/macs3/broad_peak/consensus/consensus_peaks.mLb.clN.saf` | features 1934 → 1934; shared=1934 |
| `chromap/merged_library/macs3/broad_peak/qc/D28P_REP1.mLb.clN_peaks.FRiP_mqc.tsv` | 1 exact field differences |
| `chromap/merged_library/macs3/broad_peak/qc/D28_REP1.mLb.clN_peaks.FRiP_mqc.tsv` | 0 exact field differences |
| `chromap/merged_library/picard_metrics/D28P_REP1.mLb.mkD.sorted.metrics.txt` | 116 exact field differences |
| `chromap/merged_library/picard_metrics/D28_REP1.mLb.mkD.sorted.metrics.txt` | 111 exact field differences |
| `chromap/merged_library/samtools_stats/D28P_REP1.mLb.clN.sorted.bam.flagstat` | 9 exact field differences |
| `chromap/merged_library/samtools_stats/D28P_REP1.mLb.clN.sorted.bam.idxstats` | 2 exact field differences |
| `chromap/merged_library/samtools_stats/D28P_REP1.mLb.clN.sorted.bam.stats` | 354 exact field differences |
| `chromap/merged_library/samtools_stats/D28P_REP1.mLb.mkD.sorted.bam.flagstat` | 12 exact field differences |
| `chromap/merged_library/samtools_stats/D28P_REP1.mLb.mkD.sorted.bam.idxstats` | 5 exact field differences |
| `chromap/merged_library/samtools_stats/D28P_REP1.mLb.mkD.sorted.bam.stats` | 1 exact field differences |
| `chromap/merged_library/samtools_stats/D28_REP1.mLb.clN.sorted.bam.flagstat` | 0 exact field differences |
| `chromap/merged_library/samtools_stats/D28_REP1.mLb.clN.sorted.bam.idxstats` | 0 exact field differences |
| `chromap/merged_library/samtools_stats/D28_REP1.mLb.clN.sorted.bam.stats` | 393 exact field differences |
| `chromap/merged_library/samtools_stats/D28_REP1.mLb.mkD.sorted.bam.flagstat` | 10 exact field differences |
| `chromap/merged_library/samtools_stats/D28_REP1.mLb.mkD.sorted.bam.idxstats` | 6 exact field differences |
| `chromap/merged_library/samtools_stats/D28_REP1.mLb.mkD.sorted.bam.stats` | 1 exact field differences |
| `pipeline_info/nf_core_atacseq_software_mqc_versions.yml` | 13 exact field differences |

## base_vs_unfixed

Matched artifacts: 24; unmatched/unreadable: 0.

| Artifact | Observed comparison |
|---|---|
| `chromap/merged_library/bigwig/scale/D28P_REP1.mLb.clN.scale_factor.txt` | 1 exact field differences |
| `chromap/merged_library/bigwig/scale/D28_REP1.mLb.clN.scale_factor.txt` | 1 exact field differences |
| `chromap/merged_library/macs3/broad_peak/D28P_REP1.mLb.clN_peaks.broadPeak` | intervals 1431 → 1436; exact Jaccard=0.791875; bp Jaccard=0.9881999859351278; peak value changes=4453 |
| `chromap/merged_library/macs3/broad_peak/D28_REP1.mLb.clN_peaks.broadPeak` | intervals 1635 → 1406; exact Jaccard=0.1837290774620475; bp Jaccard=0.8171101776199919; peak value changes=3741 |
| `chromap/merged_library/macs3/broad_peak/consensus/consensus_peaks.mLb.clN.bed` | intervals 1934 → 1800; exact Jaccard=0.3397918909221385; bp Jaccard=0.8954226802405175; peak value changes=0 |
| `chromap/merged_library/macs3/broad_peak/consensus/consensus_peaks.mLb.clN.featureCounts.tsv` | counts equal=False; intervals 1934 → 1800; changed cells=663; versions v2.0.1 → v2.0.1; D28P_REP1: total 121568 → 118648, changed shared intervals 291; D28_REP1: total 119315 → 114970, changed shared intervals 372 |
| `chromap/merged_library/macs3/broad_peak/consensus/consensus_peaks.mLb.clN.saf` | features 1934 → 1800; shared=947 |
| `chromap/merged_library/macs3/broad_peak/qc/D28P_REP1.mLb.clN_peaks.FRiP_mqc.tsv` | 1 exact field differences |
| `chromap/merged_library/macs3/broad_peak/qc/D28_REP1.mLb.clN_peaks.FRiP_mqc.tsv` | 1 exact field differences |
| `chromap/merged_library/picard_metrics/D28P_REP1.mLb.mkD.sorted.metrics.txt` | 7 exact field differences |
| `chromap/merged_library/picard_metrics/D28_REP1.mLb.mkD.sorted.metrics.txt` | 7 exact field differences |
| `chromap/merged_library/samtools_stats/D28P_REP1.mLb.clN.sorted.bam.flagstat` | 9 exact field differences |
| `chromap/merged_library/samtools_stats/D28P_REP1.mLb.clN.sorted.bam.idxstats` | 17 exact field differences |
| `chromap/merged_library/samtools_stats/D28P_REP1.mLb.clN.sorted.bam.stats` | 1 exact field differences |
| `chromap/merged_library/samtools_stats/D28P_REP1.mLb.mkD.sorted.bam.flagstat` | 12 exact field differences |
| `chromap/merged_library/samtools_stats/D28P_REP1.mLb.mkD.sorted.bam.idxstats` | 16 exact field differences |
| `chromap/merged_library/samtools_stats/D28P_REP1.mLb.mkD.sorted.bam.stats` | 1 exact field differences |
| `chromap/merged_library/samtools_stats/D28_REP1.mLb.clN.sorted.bam.flagstat` | 9 exact field differences |
| `chromap/merged_library/samtools_stats/D28_REP1.mLb.clN.sorted.bam.idxstats` | 17 exact field differences |
| `chromap/merged_library/samtools_stats/D28_REP1.mLb.clN.sorted.bam.stats` | 1 exact field differences |
| `chromap/merged_library/samtools_stats/D28_REP1.mLb.mkD.sorted.bam.flagstat` | 12 exact field differences |
| `chromap/merged_library/samtools_stats/D28_REP1.mLb.mkD.sorted.bam.idxstats` | 17 exact field differences |
| `chromap/merged_library/samtools_stats/D28_REP1.mLb.mkD.sorted.bam.stats` | 1 exact field differences |
| `pipeline_info/nf_core_atacseq_software_mqc_versions.yml` | 13 exact field differences |

## fixed_vs_unfixed

Matched artifacts: 24; unmatched/unreadable: 0.

| Artifact | Observed comparison |
|---|---|
| `chromap/merged_library/bigwig/scale/D28P_REP1.mLb.clN.scale_factor.txt` | 1 exact field differences |
| `chromap/merged_library/bigwig/scale/D28_REP1.mLb.clN.scale_factor.txt` | 1 exact field differences |
| `chromap/merged_library/macs3/broad_peak/D28P_REP1.mLb.clN_peaks.broadPeak` | intervals 1431 → 1436; exact Jaccard=0.791875; bp Jaccard=0.9881999859351278; peak value changes=4452 |
| `chromap/merged_library/macs3/broad_peak/D28_REP1.mLb.clN_peaks.broadPeak` | intervals 1635 → 1406; exact Jaccard=0.1837290774620475; bp Jaccard=0.8171101776199919; peak value changes=3741 |
| `chromap/merged_library/macs3/broad_peak/consensus/consensus_peaks.mLb.clN.bed` | intervals 1934 → 1800; exact Jaccard=0.3397918909221385; bp Jaccard=0.8954226802405175; peak value changes=0 |
| `chromap/merged_library/macs3/broad_peak/consensus/consensus_peaks.mLb.clN.featureCounts.tsv` | counts equal=False; intervals 1934 → 1800; changed cells=663; versions v2.0.1 → v2.0.1; D28P_REP1: total 121567 → 118648, changed shared intervals 291; D28_REP1: total 119315 → 114970, changed shared intervals 372 |
| `chromap/merged_library/macs3/broad_peak/consensus/consensus_peaks.mLb.clN.saf` | features 1934 → 1800; shared=947 |
| `chromap/merged_library/macs3/broad_peak/qc/D28P_REP1.mLb.clN_peaks.FRiP_mqc.tsv` | 1 exact field differences |
| `chromap/merged_library/macs3/broad_peak/qc/D28_REP1.mLb.clN_peaks.FRiP_mqc.tsv` | 1 exact field differences |
| `chromap/merged_library/picard_metrics/D28P_REP1.mLb.mkD.sorted.metrics.txt` | 7 exact field differences |
| `chromap/merged_library/picard_metrics/D28_REP1.mLb.mkD.sorted.metrics.txt` | 7 exact field differences |
| `chromap/merged_library/samtools_stats/D28P_REP1.mLb.clN.sorted.bam.flagstat` | 9 exact field differences |
| `chromap/merged_library/samtools_stats/D28P_REP1.mLb.clN.sorted.bam.idxstats` | 17 exact field differences |
| `chromap/merged_library/samtools_stats/D28P_REP1.mLb.clN.sorted.bam.stats` | 1 exact field differences |
| `chromap/merged_library/samtools_stats/D28P_REP1.mLb.mkD.sorted.bam.flagstat` | 12 exact field differences |
| `chromap/merged_library/samtools_stats/D28P_REP1.mLb.mkD.sorted.bam.idxstats` | 17 exact field differences |
| `chromap/merged_library/samtools_stats/D28P_REP1.mLb.mkD.sorted.bam.stats` | 1 exact field differences |
| `chromap/merged_library/samtools_stats/D28_REP1.mLb.clN.sorted.bam.flagstat` | 9 exact field differences |
| `chromap/merged_library/samtools_stats/D28_REP1.mLb.clN.sorted.bam.idxstats` | 17 exact field differences |
| `chromap/merged_library/samtools_stats/D28_REP1.mLb.clN.sorted.bam.stats` | 1 exact field differences |
| `chromap/merged_library/samtools_stats/D28_REP1.mLb.mkD.sorted.bam.flagstat` | 12 exact field differences |
| `chromap/merged_library/samtools_stats/D28_REP1.mLb.mkD.sorted.bam.idxstats` | 18 exact field differences |
| `chromap/merged_library/samtools_stats/D28_REP1.mLb.mkD.sorted.bam.stats` | 1 exact field differences |
| `pipeline_info/nf_core_atacseq_software_mqc_versions.yml` | 1 exact field differences |

All changed cells, interval sets, field values, per-library metrics and source hashes are retained in `comparison.json`.

- Completeness means observed completion and comparison coverage, never scientific PASS or proof the pipeline is bug-free.
- Coordinate/sample joins ignore unstable peak/GeneIDs and column order; exact numeric differences have no arbitrary tolerance.
- BED coordinates are zero-based half-open; SAF/count coordinates are one-based inclusive and compared in their own conventions.
- FRiP uses published MultiQC-custom values; duplicate-flag metrics and cleaned BAM flagstats are distinct stages.
- BigWig tracks, HOMER annotations, HTML/PDF plots and full BAM record equivalence are not semantically compared here.
- Optional QC was disabled equally; these selected read subsets support no biological differential inference.
