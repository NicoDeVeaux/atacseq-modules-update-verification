# Task: Verify nf-core/atacseq PRs #448 and #452 with a real-data A/B run

## Goal

Re-run the **HIV MDDC** dataset (GRCh38, four samples from PubMed ID
31968263) on the current head of each PR branch, and confirm the scientific
outputs still match the baseline recorded in the PR #448 description. The
purpose is to re-validate the verification claim after new commits landed on
the branches.

## The two PRs under test

Both PRs target `nf-core/atacseq:dev`. **Both PR head branches live on the
fork `NicoDeVeaux/atacseq-nfcore`, not on `nf-core/atacseq`.** This matters
for launching: point the pipeline at the fork and use the branch name (or the
pinned SHA below) as the revision.

| PR   | Title                                             | Branch (on fork `NicoDeVeaux/atacseq-nfcore`) | Head SHA at time of writing                |
|------|---------------------------------------------------|-----------------------------------------------|--------------------------------------------|
| #448 | nf-core modules update                            | `nf-core-modules-update`                      | `5caa50bfa325daa9af6feede2d3b4cf45b456d5e` |
| #452 | count mixed SE/PE libraries per-batch instead of pinning subread | `fix/featurecounts-mixed-se-pe`  | `755632c17a94e034dda0b0e1e9b92213c325c84c` |

> Re-fetch the current head SHAs before running — these branches are active
> and may have moved:
> ```bash
> gh pr view 448 --repo nf-core/atacseq --json headRefOid --jq .headRefOid
> gh pr view 452 --repo nf-core/atacseq --json headRefOid --jq .headRefOid
> ```

## Baseline to reproduce (from the PR #448 verification claim)

**HIV MDDC (GRCh38, four samples from PubMed ID 31968263)** — outputs were
reported bit-identical between the branch and `dev`:

- Per-library peak counts: **30,438 / 35,854 / 36,551 / 51,633**
- FRiP scores: **0.216448 / 0.230010 / 0.198316 / 0.250963**
- Merged-library consensus peak set: **74,895** peaks
- Merged-replicate consensus peak set: **115,880** peaks

A run **passes** if every per-library and per-replicate peak count and FRiP
score matches to full precision, and the two consensus peak-set totals match
(74,895 and 115,880).

(The PR also references an "Osmotic SRR" four-sample public subset that
produced a 72-process DAG / 185 tasks with MULTIQC as the terminal node,
confirming the topic-channel deadlock fix. Reproducing that is a secondary,
optional check — the HIV MDDC bit-identity is the primary gate.)

## What the agent should do

1. **Confirm Platform target and workspace.**
   - The original dev runs were in workspace **`cascade-t2d-discovery`**
     (org `ACME_Pharmaceuticals`) on **cloud-dev** (`cloud.dev-seqera.io`),
     using real us-east-1 S3 FASTQs. Prefer this path: it allows cloning the
     original launch config (the `prickly_cuvier` run, `3ElxrEftYMoykL`) and
     only bumping the revision.
   - If running elsewhere (e.g. `sasha-dagayev-wsp` on `cloud.seqera.io`),
     see the "Known blockers" section — a valid GitHub credential and a
     region-appropriate compute environment are required.

2. **Verify prerequisites before launching:**
   - Compute environment is `AVAILABLE`, in the same region as the input
     data, with `maxCpus` high enough for the ~185-task DAG (the CE used
     previously had maxCpus 1000, Wave + Fusion enabled).
   - A **working GitHub credential** with `repo` scope that can read the fork
     `NicoDeVeaux/atacseq-nfcore`. Confirm it resolves the repo — a stored
     credential marked `AVAILABLE` can still be an expired token (see
     blockers).
   - The input samplesheet is reachable from the compute environment.

3. **Launch two runs**, identical except for revision, writing to separate
   output dirs so results can be diffed cleanly:
   - `pipeline`: `https://github.com/NicoDeVeaux/atacseq-nfcore`
   - `revision`: `nf-core-modules-update` (#448) / `fix/featurecounts-mixed-se-pe` (#452)
   - `--genome GRCh38`
   - `input`: the HIV MDDC four-sample samplesheet (PubMed 31968263)
   - `outdir`: `.../pr448/results` and `.../pr452/results`
   - profile: `docker` (or the profile the target CE expects)

4. **After each launch call succeeds, immediately check run status** — do not
   report success until the workflow reaches a healthy running/completed
   state. If it fails, surface the failure details.

5. **When both runs complete, compare against the baseline:**
   - Pull each run's peak counts, FRiP scores, and consensus peak-set totals.
   - Compare to the four numbers above. Report per-library and per-replicate
     matches to full precision and both consensus totals.
   - The MultiQC report is the easiest single source for peak / FRiP numbers;
     fetch it per run.

6. **Report** a clear pass/fail per PR, with the actual numbers next to the
   expected numbers, and links to both runs on the Platform.

## Known blockers (encountered in a prior attempt on `cloud.seqera.io`)

- **Expired GitHub credential.** The only GitHub credential in
  `sasha-dagayev-wsp` (`github_democli`, GitHub user `odagayev`) reported
  `status: AVAILABLE` but launches failed with *"Unknown pipeline repository
  or expired Git credentials"* for **both** the public `nf-core/atacseq` and
  the fork — indicating the stored PAT is expired (a `lastUsed` bump only
  means Platform attempted the token, not that it succeeded). Resolution:
  refresh the PAT (needs `repo` scope) or add a new GitHub credential, then
  relaunch.
- **Cross-region / workspace access.** The original data lives in us-east-1
  and the dev runs were in `cascade-t2d-discovery` (org `ACME_Pharmaceuticals`).
  Make sure the launching account is a **member** of that workspace and the CE
  is in the matching region, or a public-samplesheet substitution will be
  needed and data-locality benefits are lost.

## Progress log (2026-08-22, run on `cloud.dev-seqera.io`)

**Target:** workspace `cascade-t2d-discovery` (`269037456042199`), org
`ACME_Pharmaceuticals` — the preferred path in step 1.

**Head SHAs re-fetched (unchanged from table above):**
- #448 `nf-core-modules-update` → `5caa50bfa325daa9af6feede2d3b4cf45b456d5e`
- #452 `fix/featurecounts-mixed-se-pe` → `755632c17a94e034dda0b0e1e9b92213c325c84c`

**Credential blocker — RESOLVED.** The fork is read via
`git_readonly_NicoDeVeaux` (`2VhfvaX8QgVPNQurZPxRJq`), a GitHub credential
scoped to `baseUrl: https://github.com/NicoDeVeaux` (user `NicoDeVeaux`),
created in the UI (the MCP create path can't set `baseUrl`). Both launch
attempts resolved the fork and generated a valid `nextflow run ...` command
line, confirming the token works. Note: a read-only PAT was pasted in
plaintext during the session — consider rotating it.

**Samplesheet substitution.** Using a public pinned raw URL instead of the
private us-east-1 FASTQs:
`https://raw.githubusercontent.com/NicoDeVeaux/atacseq-modules-update-verification/32d23c8f2acce102b3f5a97c44dd8edf530b1731/inputs/hiv_mddc_public_samplesheet.csv`
(verified reachable, 200, 4 samples). ✅ Confirmed identical to the HIV MDDC
claim set (PubMed 31968263): same accessions — `SRR8508547`/`SRR8508548`
(HIV_CD86HI_48H rep1/2) and `SRR8508553`/`SRR8508554` (MOCK_48H rep1/2), labels
matching the verification bundle. Same reads by accession, re-downloaded from
EBI rather than the identical staged us-east-1 S3 objects — a valid bit-identity
check for a deterministic pipeline. Peak/FRiP/consensus comparison remains the
**primary gate**. All four samples are **paired-end**, so #452's SE/PE split
should collapse to the all-PE path and match #448 bit-for-bit.

**Compute environment — swapped after a head-job failure.**
- `aws_batch_rnaseq_large` (`2hN0iEE2zNah6QdsKJYn2a`, 256 CPUs) — **FAILED at
  startup.** First #448 run `sharp_tesla` (`oxXhNRUsHx2a6`) went `FAILED`
  within ~1 min: 0 processes, no `.nextflow.log` in S3 (`specified key does
  not exist`) = the AWS Batch **head job never started**. CE had been idle
  since 2026-03-25; stale SPOT/launch-template state is the likely cause.
- `aws_batch_fusion` (`5iXBHxvoZN3qP8cx9C7CLI`, maxCpus **20**, Wave+Fusion,
  last used 2026-08-12) — relaunched here. Lower CPU ceiling → the ~185-task
  DAG runs more serialized and slower, but it starts cleanly.

**Runs launched (shared workDir `s3://a-test-bucket-eend-us-east-1/atacseq-verify/work`):**

| PR   | Run name           | Run ID           | Session                                | CE                 | Status (last checked)     | outdir                  |
|------|--------------------|------------------|----------------------------------------|--------------------|---------------------------|-------------------------|
| #448 | `sharp_tesla`      | `oxXhNRUsHx2a6`  | `1519de8c-...`                         | rnaseq_large       | FAILED (head-job start)   | `.../pr448/results`     |
| #448 | `golden_mandelbrot`| `1ydNwxfh6zreRj` | `31b6a2c4-bc38-40a7-8716-2849672fb60c` | aws_batch_fusion   | SUBMITTED → monitoring    | `.../pr448/results`     |
| #452 | —                  | —                | (resume from `31b6a2c4`)               | aws_batch_fusion   | pending #448 completion   | `.../pr452/results`     |

Run URL (#448 active):
https://cloud.dev-seqera.io/orgs/ACME_Pharmaceuticals/workspaces/cascade-t2d-discovery/watch/1ydNwxfh6zreRj

**Next steps:**
1. Monitor `golden_mandelbrot` to `SUCCEEDED` (MULTIQC terminal node).
2. Launch #452 (`fix/featurecounts-mixed-se-pe`) with **resume** from session
   `31b6a2c4` on the same workDir, `outdir .../pr452/results`.
3. Fetch each run's MultiQC report; compare per-library/per-replicate peak
   counts + FRiP and both consensus totals (74,895 / 115,880) to baseline;
   report pass/fail per PR with URLs.

## Offline verification analysis (2026-08-22, later session)

Live run status could **not** be refreshed this session: all Seqera Platform
API calls returned **HTTP 401** (`/workflow`, `/workflow/1ydNwxfh6zreRj`,
`/workflow/.../progress`) — the Platform token is expired and needs re-auth.
`gh` and the public data lookups use separate auth and worked fine. The work
below was therefore done **offline against the downloaded run outputs** staged
under `/tmp/amuv-inspect/verification/` (branch + dev consensus outputs from the
verification bundle), plus freshly retrieved original-paper data.

Head SHAs re-fetched this session (unchanged):
- #448 `nf-core-modules-update` → `5caa50bfa325daa9af6feede2d3b4cf45b456d5e`
- #452 `fix/featurecounts-mixed-se-pe` → `755632c17a94e034dda0b0e1e9b92213c325c84c`

### Finding 1 (HEADLINE) — consensus counts ~1.92× inflated on the branch

The modules update bumps **featureCounts v2.0.1 (dev) → v2.1.1 (branch)**. Over
the 69,596 consensus intervals shared by exact coordinate, every sample's total
read count **roughly doubles** (Pearson r ≈ 0.9996 — a near-uniform proportional
scaling, not noise):

| Sample | dev total | branch total | ratio |
|--------|----------:|-------------:|------:|
| HIV_CD86HI_48H_REP1 | 755,472 | 1,445,223 | 1.91× |
| HIV_CD86HI_48H_REP2 | 1,049,186 | 2,018,283 | 1.92× |
| MOCK_48H_REP1 | 728,326 | 1,391,601 | 1.91× |
| MOCK_48H_REP2 | 1,207,245 | 2,327,082 | 1.93× |

**Most likely cause — subread `-p` semantics change (fragments → reads).** Both
arms call featureCounts with identical flags (`-F SAF -O --fracOverlap 0.2 -p -s 0`)
and **neither** passes `--countReadPairs`. In subread **< 2.0.2** (dev's v2.0.1)
`-p` counts *fragments*; from **2.0.2 onward** (branch's v2.1.1) `-p` only declares
paired-end input and counts *individual reads* unless `--countReadPairs` is added.
The consistent ~1.92× matches counting both mates instead of one fragment.

> This is the single most probable explanation given the version boundary + the
> ~2× signature; it was **not** confirmed by re-running featureCounts. **Action
> for the PR:** add `--countReadPairs` to the featureCounts invocation to preserve
> fragment-level consensus counts (keeps DESeq2 size factors and published numbers
> comparable), or explicitly document the switch to read-level counting.

This contradicts the "outputs bit-identical between branch and dev" verification
claim at the **count** level, even though peak *locations* are ~unchanged
(Finding 3).

### Finding 2 — `comparison.tsv` under-reports the consensus difference

The bundle's `verification/comparison.tsv` lists the `mLb.clN` consensus as
**74,895 peaks for both arms**. The actual branch consensus output has
**74,935** (dev 74,895). `comparison.tsv` should be regenerated/annotated.

### Finding 3 — original-paper peaks located; build is GRCh38 (no liftOver)

- Study **SRP182967** = GEO **GSE125918** (ATAC-seq) / **GSE125919** (SuperSeries),
  De Veaux et al., PubMed 31968263.
- Gold-standard peak set = **87,681 Peakdeck peaks**, published as
  `GSE125918_Table_S3_ATAC_peak_RLOG_counts.txt.gz` (series supplementary). File
  uses legacy `\r` line endings; normalized to 87,681 rows (chrom/start/end + rlog
  counts per sample).
- **Build determination: GRCh38/hg38, NOT hg19** — decisive evidence is chr20,
  whose max peak end (64,286,330) **exceeds hg19 chr20 length** (63,025,520) but
  fits hg38 chr20 (64,444,167); chr2/chr8 maxima sit within ~80 kb of the hg38
  chromosome ends but ~1 Mb short of hg19. GEO's `Genome_build: hg19; hg38` is
  thus resolved to hg38 for this table.
- **Consequence:** the planned hg19→GRCh38 liftOver is **unnecessary** — the
  original peaks are already on the same build (and `chr`-style naming) as the
  new runs, so they intersect directly.

### Finding 4 — peak-overlap: dev ≈ branch; reasonable concordance vs paper

Overlap computed by merging all sets into disjoint GRCh38 **union regions** and
scoring membership (≥1 bp):

| Set | Raw peaks | Union regions |
|-----|----------:|--------------:|
| paper_original | 87,681 | 84,183 |
| dev | 74,895 | 74,449 |
| branch | 74,935 | 74,486 |

- **dev vs branch: Jaccard 0.995**, reciprocal 99.7–99.8% — the modules update
  barely changes *which* regions are peaks. The regression is in the **counts**
  (Finding 1), not in peak calling.
- **paper vs pipeline: Jaccard ~0.564**; 57,129 regions shared by all three;
  26,927 paper-only (Peakdeck p<1e-4 on all merged conditions is more permissive
  than the nf-core MACS2 4-sample subset); ~77% of pipeline peaks overlap the
  paper set, ~69% of paper peaks recovered. Reasonable cross-tool concordance.

### Re-runnable artifacts (under `/tmp/amuv-inspect/verification/`)

All tools are pure Python stdlib (no bedtools/matplotlib), driven by manifests,
and adapt to any number of arms — **just add `pr448`/`pr452` rows and re-run**:

- `scripts/compare_featurecounts.py` + `counts/manifest.tsv` → `counts/COUNT_CHANGES.md`,
  `counts/count_changes.*.tsv`, `counts/README.md` (interpretation). Coord-keyed,
  name-matched columns.
- `scripts/peak_overlap.py` + `overlap/manifest.tsv` → `overlap/PEAK_OVERLAP.md`,
  `overlap/peak_overlap_upset.svg` (UpSet figure), `overlap/peak_overlap_combos.tsv`.
- Original peaks: `overlap/data/paper_original/paper_peaks.GRCh38.bed` (+ the raw
  Table S3 and normalized TSV).

### Updated next steps

1. **Re-authenticate Seqera Platform** (token 401), then check `golden_mandelbrot`
   (`1ydNwxfh6zreRj`) status and launch #452 as previously planned.
2. **Raise Finding 1 on PR #448** — the `--countReadPairs`/fragment-vs-read
   question is the material scientific change; the "bit-identical" claim needs
   qualifying (identical peak locations, but ~2× counts).
3. When PR #448/#452 runs finish, drop their `consensus_peaks.mLb.clN.featureCounts.*`
   and `.bed` into `counts/pr448/`,`overlap/data/pr448/` (etc.), uncomment the
   manifest rows, and re-run both tools for a 4–5-way comparison including the paper.

## Progress log (2026-08-22, run on `cloud.dev-seqera.io`)

**Target:** workspace `cascade-t2d-discovery` (`269037456042199`), org
`ACME_Pharmaceuticals` — the preferred path in step 1.

**Head SHAs re-fetched (unchanged from table above):**
- #448 `nf-core-modules-update` → `5caa50bfa325daa9af6feede2d3b4cf45b456d5e`
- #452 `fix/featurecounts-mixed-se-pe` → `755632c17a94e034dda0b0e1e9b92213c325c84c`

**Credential blocker — RESOLVED.** The fork is read via
`git_readonly_NicoDeVeaux` (`2VhfvaX8QgVPNQurZPxRJq`), a GitHub credential
scoped to `baseUrl: https://github.com/NicoDeVeaux` (user `NicoDeVeaux`),
created in the UI (the MCP create path can't set `baseUrl`). Both launch
attempts resolved the fork and generated a valid `nextflow run ...` command
line, confirming the token works. Note: a read-only PAT was pasted in
plaintext during the session — consider rotating it.

**Samplesheet substitution.** Using a public pinned raw URL instead of the
private us-east-1 FASTQs:
`https://raw.githubusercontent.com/NicoDeVeaux/atacseq-modules-update-verification/32d23c8f2acce102b3f5a97c44dd8edf530b1731/inputs/hiv_mddc_public_samplesheet.csv`
(verified reachable, 200, 4 samples). ✅ Confirmed identical to the HIV MDDC
claim set (PubMed 31968263): same accessions — `SRR8508547`/`SRR8508548`
(HIV_CD86HI_48H rep1/2) and `SRR8508553`/`SRR8508554` (MOCK_48H rep1/2), labels
matching the verification bundle. Same reads by accession, re-downloaded from
EBI rather than the identical staged us-east-1 S3 objects — a valid bit-identity
check for a deterministic pipeline. Peak/FRiP/consensus comparison remains the
**primary gate**. All four samples are **paired-end**, so #452's SE/PE split
should collapse to the all-PE path and match #448 bit-for-bit.

**Compute environment — swapped after a head-job failure.**
- `aws_batch_rnaseq_large` (`2hN0iEE2zNah6QdsKJYn2a`, 256 CPUs) — **FAILED at
  startup.** First #448 run `sharp_tesla` (`oxXhNRUsHx2a6`) went `FAILED`
  within ~1 min: 0 processes, no `.nextflow.log` in S3 (`specified key does
  not exist`) = the AWS Batch **head job never started**. CE had been idle
  since 2026-03-25; stale SPOT/launch-template state is the likely cause.
- `aws_batch_fusion` (`5iXBHxvoZN3qP8cx9C7CLI`, maxCpus **20**, Wave+Fusion,
  last used 2026-08-12) — relaunched here. Lower CPU ceiling → the ~185-task
  DAG runs more serialized and slower, but it starts cleanly.

**Runs launched (shared workDir `s3://a-test-bucket-eend-us-east-1/atacseq-verify/work`):**

| PR   | Run name           | Run ID           | Session                                | CE                 | Status (last checked)     | outdir                  |
|------|--------------------|------------------|----------------------------------------|--------------------|---------------------------|-------------------------|
| #448 | `sharp_tesla`      | `oxXhNRUsHx2a6`  | `1519de8c-...`                         | rnaseq_large       | FAILED (head-job start)   | `.../pr448/results`     |
| #448 | `golden_mandelbrot`| `1ydNwxfh6zreRj` | `31b6a2c4-bc38-40a7-8716-2849672fb60c` | aws_batch_fusion   | SUBMITTED → monitoring    | `.../pr448/results`     |
| #452 | —                  | —                | (resume from `31b6a2c4`)               | aws_batch_fusion   | pending #448 completion   | `.../pr452/results`     |

Run URL (#448 active):
https://cloud.dev-seqera.io/orgs/ACME_Pharmaceuticals/workspaces/cascade-t2d-discovery/watch/1ydNwxfh6zreRj

**Next steps:**
1. Monitor `golden_mandelbrot` to `SUCCEEDED` (MULTIQC terminal node).
2. Launch #452 (`fix/featurecounts-mixed-se-pe`) with **resume** from session
   `31b6a2c4` on the same workDir, `outdir .../pr452/results`.
3. Fetch each run's MultiQC report; compare per-library/per-replicate peak
   counts + FRiP and both consensus totals (74,895 / 115,880) to baseline;
   report pass/fail per PR with URLs.

## Definition of done

- Both PR branches launched at their current head on a healthy CE.
- Both runs completed successfully with MULTIQC as the terminal node.
- HIV MDDC peak counts, FRiP scores, and both consensus peak-set totals
  reported side-by-side with the baseline, with an explicit pass/fail per PR.
- Platform run URLs included for both.
