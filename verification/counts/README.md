# Consensus count changes (dev vs branch)

This directory quantifies how the **consensus featureCounts** output changes between
upstream `dev` and the `nf-core-modules-update` branch, on the all-paired-end HIV MDDC
cohort. It is generated from the actual pipeline output files, independent of the
top-level `comparison.tsv`.

- **Inputs:** `dev/consensus_peaks.mLb.clN.featureCounts.txt`,
  `branch/consensus_peaks.mLb.clN.featureCounts.tsv`
- **Tool:** `../scripts/compare_featurecounts.py` (stdlib only)
- **Generated table:** `COUNT_CHANGES.md` + `count_changes.dev_vs_branch.tsv`
- **Re-run** (adds `pr448` / `pr452` automatically once their files are dropped in and
  uncommented in `manifest.tsv`):

  ```bash
  python3 verification/scripts/compare_featurecounts.py \
      --manifest verification/counts/manifest.tsv --baseline dev --outdir verification/counts
  ```

## Headline findings

1. **featureCounts version bump: `v2.0.1` (dev) → `v2.1.1` (branch)** — introduced by the
   modules update.

2. **Read counts roughly double.** Per-sample totals over shared intervals:

   | Sample | dev total | branch total | ratio |
   |--------|----------:|-------------:|------:|
   | HIV_CD86HI_48H_REP1 | 755,472 | 1,445,223 | 1.91× |
   | HIV_CD86HI_48H_REP2 | 1,049,186 | 2,018,283 | 1.92× |
   | MOCK_48H_REP1 | 728,326 | 1,391,601 | 1.91× |
   | MOCK_48H_REP2 | 1,207,245 | 2,327,082 | 1.93× |

   Pearson r ≈ 0.9996 for every sample: the change is a near-uniform proportional scaling,
   not random noise.

3. **Confirmed cause — subread `-p` semantics change (fragments → reads).**
   Both arms invoke featureCounts with identical flags: `-F SAF -O --fracOverlap 0.2 -p -s 0`,
   **neither** passes `--countReadPairs`. In subread **< 2.0.2** (dev's v2.0.1), `-p` counts
   *fragments* (read pairs). From subread **2.0.2 onward** (branch's v2.1.1), `-p` only
   declares paired-end input and counts *individual reads* unless `--countReadPairs` is added.
   The consistent ~1.92× inflation matches counting both mates instead of one fragment.

   This is **confirmed** by two independent checks: (a) the command lines recorded in both
   count matrices are byte-for-byte identical except the version string — same flags, no
   `--countReadPairs` on either — so the subread version is the only variable; and (b) a
   direct re-run of subread **v2.1.1** featureCounts on a real paired-end BAM flips the
   header from `Count read pairs: no` (reads) to `Count read pairs: yes` (fragments) when
   `--countReadPairs` is added, roughly halving the assigned total (~1.76× on a small noisy
   test BAM, ~1.92× on the cleaner HIV MDDC data).

   **Implication for the PR:** to preserve fragment-level consensus counts (and keep DESeq2
   size factors / downstream numbers comparable to dev and to the published analysis), the
   featureCounts module invocation should add `--countReadPairs`. If the switch to read-level
   counting is intentional, it should be called out explicitly, because it changes every
   consensus count. **Neither open PR currently fixes this:** #448 introduces the version
   bump that triggers it, and #452 leaves the `-p`-only invocation intact
   (`grep -rn countReadPairs` returns zero hits on both heads). The fix is a one-liner in
   `modules/nf-core/subread/featurecounts/main.nf`:
   `def paired_end = meta.single_end ? '' : '-p --countReadPairs'`.

4. **The consensus peak set also shifted.** dev has 74,895 intervals, branch 74,935. Keyed by
   exact coordinate, 69,596 are shared, with 5,299 unique to dev and 5,339 unique to branch.
   Many "unique" intervals are the same peak with boundaries shifted by a few bp (exact-coord
   keying is strict); true reciprocal-overlap concordance is measured by the peak-overlap
   visualization under `../overlap/`.

## Discrepancy with `comparison.tsv`

The bundle's `verification/comparison.tsv` reports the `mLb.clN` consensus as **74,895 peaks
for both arms**. The actual branch consensus output has **74,935**. `comparison.tsv` therefore
under-reports a real 40-peak (net) difference at the consensus level and should be regenerated
or annotated.

## Scope note on #452

Both verification cohorts are all-paired-end, so PR #452 (mixed SE/PE per-batch counting)
produces no change here by construction. Its effect requires a mixed SE/PE cohort. The tool
and manifest are ready to quantify it as soon as a `pr452` featureCounts file is available.
