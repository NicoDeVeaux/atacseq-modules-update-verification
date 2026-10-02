# RESUME — nf-core/atacseq PR #448/#452 verification

**Checkpoint saved:** 2026-08-23 03:55. Pick this up tomorrow.

This is the quick-start / handoff. The full task spec + detailed findings live in
`~/Dev/portal/atacseq-pr-verification-task.md` (section: *Offline verification
analysis (2026-08-22, later session)*). All analysis artifacts + tools are now in
`~/Dev/atacseq-pr-verification/` (copied out of `/tmp`, which can be wiped on reboot).

---

## TL;DR — where things stand

- **Offline analysis of the already-downloaded dev/branch outputs: DONE.**
- **Original-paper data: retrieved, and the planned liftOver turned out unnecessary.**
- **Live Platform runs: BLOCKED — Seqera token was 401 all session.** Could not
  refresh `golden_mandelbrot` (#448) status or launch #452.

### The one finding that matters most
PR #448 bumps **featureCounts v2.0.1 → v2.1.1**, and consensus read counts
**~double** (1.91–1.93× every sample, Pearson r ≈ 0.9996). Almost certainly the
subread **≥2.0.2 `-p` semantics change**: `-p` used to count *fragments*, now
counts *individual reads* unless `--countReadPairs` is passed — and the module
passes `-p` without `--countReadPairs`. So the "outputs bit-identical" claim holds
for peak **locations** but **not** counts.
→ **Action:** flag on PR #448; suggest adding `--countReadPairs` (or documenting
the switch to read-level counting). *Inference from version boundary + 2× signature;
not yet confirmed by re-running featureCounts.*

Secondary findings:
- `comparison.tsv` says consensus = 74,895 for both arms; branch is actually **74,935** (dev 74,895).
- Original paper peaks (GSE125918 Table S3, 87,681 Peakdeck peaks) are **GRCh38, not hg19** → **no liftOver needed**.
- dev vs branch peak locations: Jaccard **0.995** (barely change). paper vs pipeline: Jaccard ~0.564, ~77% of pipeline peaks overlap paper.

---

## TODO tomorrow (in priority order)

1. **Re-authenticate Seqera Platform**, then check run `golden_mandelbrot`
   (`1ydNwxfh6zreRj`, ws `cascade-t2d-discovery` = `269037456042199`):
   ```
   https://cloud.dev-seqera.io/orgs/ACME_Pharmaceuticals/workspaces/cascade-t2d-discovery/watch/1ydNwxfh6zreRj
   ```
   If SUCCEEDED → pull its consensus outputs. If FAILED/lost → relaunch (see task doc step 3).
2. **Launch #452** (`fix/featurecounts-mixed-se-pe`, SHA `755632c1...`) with resume
   from session `31b6a2c4` on the same workDir, `outdir .../pr452/results`. (All 4
   samples are paired-end, so #452 should collapse to the all-PE path.)
3. **Raise Finding 1 on PR #448** — the fragment-vs-read / `--countReadPairs` question.
4. When #448/#452 outputs land, wire them into the comparison (commands below) for a
   4–5-way view including the paper set.

**Re-fetch head SHAs before relaunching** (branches are active):
```bash
gh pr view 448 --repo nf-core/atacseq --json headRefOid --jq .headRefOid   # was 5caa50bf...
gh pr view 452 --repo nf-core/atacseq --json headRefOid --jq .headRefOid   # was 755632c1...
```

---

## Artifacts (all under `~/Dev/atacseq-pr-verification/`)

```
scripts/compare_featurecounts.py   # coord-keyed, name-matched count comparison (stdlib only)
scripts/peak_overlap.py            # union-region overlap + UpSet SVG (stdlib only)
counts/manifest.tsv                # arms for the count comparison (root-relative paths)
counts/COUNT_CHANGES.md            # generated table (dev vs branch)
counts/README.md                   # interpretation of the ~1.92x finding
overlap/manifest.tsv               # arms for the overlap (paper/dev/branch)
overlap/PEAK_OVERLAP.md            # generated overlap tables
overlap/peak_overlap_upset.svg     # UpSet figure
overlap/data/paper_original/paper_peaks.GRCh38.bed   # original 87,681 peaks (GRCh38)
overlap/data/{dev,branch}/consensus_peaks.mLb.clN.bed
counts/{dev,branch}/consensus_peaks.mLb.clN.featureCounts.*
```
Both tools are manifest-driven and adapt to any N arms — verified runnable from
this location tonight.

### Re-run the analyses
```bash
cd ~/Dev/atacseq-pr-verification
# count comparison (writes counts/COUNT_CHANGES.md + *.tsv)
python3 scripts/compare_featurecounts.py --manifest counts/manifest.tsv --baseline dev --outdir counts
# peak overlap (writes overlap/PEAK_OVERLAP.md + peak_overlap_upset.svg)
cd overlap && python3 ../scripts/peak_overlap.py --manifest manifest.tsv --outdir . --min-overlap 1
```

### Add PR #448 / #452 once their runs finish
1. Drop each run's `consensus_peaks.mLb.clN.featureCounts.*` into `counts/pr448/` (and `pr452/`).
2. Drop each run's `consensus_peaks.mLb.clN.bed` into `overlap/data/pr448/` (and `pr452/`).
3. Uncomment the `pr448` / `pr452` lines in `counts/manifest.tsv` and `overlap/manifest.tsv`.
4. Re-run the two commands above — the tools handle 4–5 arms automatically.

---

## Key IDs / provenance (so you don't re-derive them)

- Study SRP182967 → GEO **GSE125918** (ATAC) / **GSE125919** (SuperSeries); PubMed **31968263**.
- Gold-standard peaks: `GSE125918_Table_S3_ATAC_peak_RLOG_counts.txt.gz` (series suppl; legacy `\r` line endings).
- Build proof (GRCh38 not hg19): chr20 max peak end 64,286,330 > hg19 chr20 (63,025,520), fits hg38 chr20 (64,444,167).
- #448 branch `nf-core-modules-update` @ `5caa50bfa325daa9af6feede2d3b4cf45b456d5e`
- #452 branch `fix/featurecounts-mixed-se-pe` @ `755632c17a94e034dda0b0e1e9b92213c325c84c`
- Fork read via credential `git_readonly_NicoDeVeaux` (`2VhfvaX8QgVPNQurZPxRJq`).
- CE for the active run: `aws_batch_fusion` (`5iXBHxvoZN3qP8cx9C7CLI`, maxCpus 20, Wave+Fusion).
