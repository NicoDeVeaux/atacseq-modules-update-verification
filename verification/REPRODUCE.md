# Reproducing the count & peak-overlap analysis

Self-contained, credential-free reproduction of the consensus **count-change** and
**peak-overlap** analyses for the nf-core/atacseq modules update (PR #448) and the
mixed SE/PE counting fix (PR #452). Everything runs with **Python 3.8+ stdlib only** —
no bedtools, no matplotlib, no network (except the optional GEO fetch script).

## Commit hashes

| Item | SHA |
|------|-----|
| PR #448 `nf-core-modules-update` head | `5caa50bfa325daa9af6feede2d3b4cf45b456d5e` |
| PR #452 `fix/featurecounts-mixed-se-pe` head | `755632c17a94e034dda0b0e1e9b92213c325c84c` |
| Branch A/B run commit (tree-identical to tested `52836f0`) | `0116142` |

> These branches are active; re-fetch before relaunching:
> ```bash
> gh pr view 448 --repo nf-core/atacseq --json headRefOid --jq .headRefOid
> gh pr view 452 --repo nf-core/atacseq --json headRefOid --jq .headRefOid
> ```

## Inputs committed here

- `counts/dev/consensus_peaks.mLb.clN.featureCounts.txt` — upstream `dev` matrix (featureCounts **v2.0.1**)
- `counts/branch/consensus_peaks.mLb.clN.featureCounts.tsv` — branch matrix (featureCounts **v2.1.1**)
- `overlap/data/dev/consensus_peaks.mLb.clN.bed`, `overlap/data/branch/consensus_peaks.mLb.clN.bed`
- `overlap/data/paper_original/paper_peaks.GRCh38.bed` — original paper peak set (87,681 peaks, GRCh38)

Not committed (regenerable, see below): the raw GEO `.gz` (~15 MB) and its `S3_normalized.tsv` (~33 MB).

## Run it

From the **repo root**:

```bash
# 1) Per-sample count comparison (dev vs branch)
python3 verification/scripts/compare_featurecounts.py \
    --manifest verification/counts/manifest.tsv --baseline dev --outdir verification/counts
#    -> verification/counts/COUNT_CHANGES.md, count_changes.dev_vs_branch.tsv

# 2) Peak-set overlap (paper vs dev vs branch), UpSet SVG + tables
python3 verification/scripts/peak_overlap.py \
    --manifest verification/overlap/manifest.tsv --outdir verification/overlap --min-overlap 1
#    -> verification/overlap/PEAK_OVERLAP.md, peak_overlap_upset.svg, peak_overlap_combos.tsv
```

Optional — re-fetch/regenerate the original paper peaks from GEO:

```bash
bash verification/scripts/fetch_paper_peaks.sh   # re-downloads GSE125918 Table S3, rebuilds the BED
```

## Original-paper data provenance

- Study **SRP182967** → GEO **GSE125918** (ATAC-seq) / **GSE125919** (SuperSeries).
  Johnson, De Veaux et al., *Cell Reports* 2020; PMID **31968263**.
- Gold-standard peak set: **87,681 Peakdeck peaks**, from
  `GSE125918_Table_S3_ATAC_peak_RLOG_counts.txt.gz` (series supplementary; legacy `\r` line endings).
- **Build: GRCh38/hg38, not hg19** → no liftOver needed. Proof: chr20 max peak end
  (64,286,330) exceeds hg19 chr20 length (63,025,520) but fits hg38 chr20 (64,444,167).

## Headline results

- **Counts ~2× on the branch** (v2.0.1 → v2.1.1), consistent 1.91–1.93× per sample,
  Pearson r ≈ 0.9996 — most likely the subread `-p` fragments→reads change (needs
  `--countReadPairs` to keep fragment counting). See `counts/PER_SAMPLE_COUNTS.md`.
- **Peak locations barely change**: dev vs branch Jaccard 0.995. The material change is
  in counting, not peak calling. See `overlap/PEAK_OVERLAP.md`.
- **`comparison.tsv` vs these matrices**: comparison.tsv lists consensus 74,895 for both
  arms; the branch matrix has 74,935. Reconcile against run provenance (see PER_SAMPLE_COUNTS.md).

## Extending to the PR #448 / #452 re-runs

1. Drop each run's `consensus_peaks.mLb.clN.featureCounts.*` into `counts/pr448/` (and `pr452/`).
2. Drop each run's `consensus_peaks.mLb.clN.bed` into `overlap/data/pr448/` (and `pr452/`).
3. Uncomment the `pr448` / `pr452` lines in both `manifest.tsv` files.
4. Re-run the two commands above — the tools handle any number of arms.

## Launch parameters (for the re-runs)

- pipeline: `https://github.com/NicoDeVeaux/atacseq-nfcore`
- revision: `nf-core-modules-update` (#448) / `fix/featurecounts-mixed-se-pe` (#452)
- input: `inputs/hiv_mddc_public_samplesheet.csv` (public EBI FASTQ URLs, 4 PE samples)
- `--genome GRCh38`, profile `docker` (or the target compute environment's profile)

No credentials, tokens, or private bucket names are stored in this directory.
