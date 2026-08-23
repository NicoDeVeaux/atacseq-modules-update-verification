# Consensus count changes (dev vs branch)

This directory quantifies how the **consensus featureCounts** output changes between
upstream `dev` and the `nf-core-modules-update` branch, on the all-paired-end HIV MDDC
cohort. It is generated from the actual pipeline output files, independent of the
top-level `comparison.tsv`.

- **Inputs:** `dev/consensus_peaks.mLb.clN.featureCounts.txt`,
  `branch/consensus_peaks.mLb.clN.featureCounts.tsv` (originally-tested commit, subread v2.1.1),
  `pr448/consensus_peaks.mLb.clN.featureCounts.tsv` (current head `5caa50bf`, subread v2.0.1)
- **Tool:** `../scripts/compare_featurecounts.py` (stdlib only)
- **Generated tables:** `COUNT_CHANGES.md` + `count_changes.dev_vs_branch.tsv`
  + `count_changes.dev_vs_pr448.tsv`
- **Re-run** (adds `pr452` automatically once its file is dropped in and uncommented
  in `manifest.tsv`):

  ```bash
  python3 verification/scripts/compare_featurecounts.py \
      --manifest verification/counts/manifest.tsv --baseline dev --outdir verification/counts
  ```

## Headline findings

> **Resolved on the current PR head.** The 1.9× inflation below was on the
> **originally-tested commit** (`branch`, subread v2.1.1). The **current PR #448 head**
> (`pr448`, `5caa50bf`) pins subread back to **v2.0.1** and matches `dev` to within
> **<0.1%** (see finding 3a). Findings 1–3 document the original diagnosis; 3a documents
> the fix.

1. **featureCounts version on the tested commit: `v2.0.1` (dev) → `v2.1.1` (branch)** —
   introduced by the modules update, later reverted to v2.0.1 on the current head.

2. **On the tested commit, read counts roughly doubled.** Per-sample totals over shared
   intervals:

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
   featureCounts consensus counts must stay fragment-level — either by keeping subread on
   v2.0.1, or by adding `--countReadPairs` when on v2.0.2+.

3a. **Fixed on the current PR #448 head (`5caa50bf`).** The `pr448` re-run
   (`stupefied_elion`, this commit) ships **subread v2.0.1**
   (`quay.io/biocontainers/subread:2.0.1--hed695b0_0`), so `-p` again counts fragments.
   Consensus totals now match `dev` to within **<0.1%**:

   | Sample | dev total | pr448 total | delta | ratio | Pearson r |
   |--------|----------:|------------:|------:|------:|----------:|
   | HIV_CD86HI_48H_REP1 | 755,472 | 755,866 | +394 | 1.001× | 0.999951 |
   | HIV_CD86HI_48H_REP2 | 1,049,186 | 1,049,954 | +768 | 1.001× | 0.999955 |
   | MOCK_48H_REP1 | 728,326 | 728,600 | +274 | 1.000× | 0.999956 |
   | MOCK_48H_REP2 | 1,207,245 | 1,207,725 | +480 | 1.000× | 0.999956 |

   The ~1.92× inflation is gone. Residual sub-0.1% deltas trace to the slightly different
   consensus interval set (74,935 vs 74,895) shifting a few overlaps, not systematic scaling.
   The current head does **not** add `--countReadPairs` (it fixes the inflation by staying on
   v2.0.1); if the modules are re-bumped to subread ≥ 2.0.2 later, the one-liner
   `def paired_end = meta.single_end ? '' : '-p --countReadPairs'` in
   `modules/nf-core/subread/featurecounts/main.nf` would be needed to keep fragment counting.

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
