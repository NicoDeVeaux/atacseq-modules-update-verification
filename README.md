# atacseq modules-update — verification bundle

Reviewer-facing evidence for the PR that updates nf-core modules/subworkflows in
[nf-core/atacseq](https://github.com/nf-core/atacseq) and fixes a MultiQC topic-channel
deadlock. It holds the artifacts from a real-data **A/B comparison** of the update branch
against upstream `dev`, run on two independent four-sample datasets.

**PR:** `NicoDeVeaux/atacseq:nf-core-modules-update` → `nf-core/atacseq:dev`
**Compare:** https://github.com/nf-core/atacseq/compare/dev...NicoDeVeaux:atacseq:nf-core-modules-update

---

## The four runs

All four ran on AWS Batch (Wave + Fusion, `us-east-1`) and **SUCCEEDED**. Branch runs were
executed at commit `52836f0`.

| Dataset | Arm | Run | Platform run |
|---------|-----|-----|--------------|
| HIV MDDC (GRCh38) | branch | `prickly_cuvier` | https://cloud.dev-seqera.io/orgs/ACME_Pharmaceuticals/workspaces/cascade-t2d-discovery/watch/3ElxrEftYMoykL |
| HIV MDDC (GRCh38) | dev | `silly_stonebraker` | https://cloud.dev-seqera.io/orgs/ACME_Pharmaceuticals/workspaces/cascade-t2d-discovery/watch/OtmJH9rJIz0LX |
| Osmotic SRR (public subset) | branch | `happy_monod` | https://cloud.dev-seqera.io/orgs/ACME_Pharmaceuticals/workspaces/cascade-t2d-discovery/watch/5GE2qTVi73wZwk |
| Osmotic SRR (public subset) | dev | `prickly_woese` | https://cloud.dev-seqera.io/orgs/ACME_Pharmaceuticals/workspaces/cascade-t2d-discovery/watch/3UMpJnGu3KQwO0 |

> Platform run links require membership of the `cascade-t2d-discovery` workspace. The
> artifacts in this repo are self-contained and need no Platform access.

### View the MultiQC reports in-browser

GitHub won't render HTML inline, so open the committed reports through htmlpreview:

| Dataset | branch | dev |
|---------|--------|-----|
| HIV MDDC | https://htmlpreview.github.io/?https://github.com/NicoDeVeaux/atacseq-modules-update-verification/blob/main/verification/hiv-mddc/branch/multiqc_report.html | https://htmlpreview.github.io/?https://github.com/NicoDeVeaux/atacseq-modules-update-verification/blob/main/verification/hiv-mddc/dev/multiqc_report.html |
| Osmotic SRR | https://htmlpreview.github.io/?https://github.com/NicoDeVeaux/atacseq-modules-update-verification/blob/main/verification/osmotic-srr/branch/multiqc_report.html | https://htmlpreview.github.io/?https://github.com/NicoDeVeaux/atacseq-modules-update-verification/blob/main/verification/osmotic-srr/dev/multiqc_report.html |

> htmlpreview streams the single-file report through a proxy; large MultiQC reports can be
> slow to load. For a more robust hosted view, enable GitHub Pages on this repo and link the
> reports under the Pages URL instead.

### Revision provenance
The branch A/B runs were executed at `52836f0`. That commit was later **metadata-only
rewritten** (author change) to `0116142`, which is **tree-identical** to `52836f0` — so the
code that was tested is exactly the code in the PR at that point. The only commit after it,
`b8f1b53`, is **whitespace-only** (test snapshots), with no runtime effect. `52836f0` is
therefore not present in PR history by SHA; look for `0116142`.

---

## What's here

```
inputs/
├── hiv_mddc_public_samplesheet.csv       # runnable A/B input (public EBI FASTQ URLs)
└── hiv_mddc_private_s3_samplesheet.csv    # provenance only: exact input the real-depth runs consumed (bucket redacted)
verification/
├── comparison.tsv              # machine-readable A/B peak-count + FRiP table (all runs)
├── sha256sums.txt              # integrity hashes for every artifact in this bundle
├── hiv-mddc/
│   ├── branch/multiqc_report.html
│   └── dev/multiqc_report.html
└── osmotic-srr/
    ├── branch/multiqc_report.html
    └── dev/multiqc_report.html
```

Open any `multiqc_report.html` in a browser. The peak counts and FRiP scores below are drawn
from these reports; `comparison.tsv` is the tidy version.

> **Note on execution reports.** Nextflow `trace`/`report`/`timeline`/`dag` were not
> republished here — they were not present at a uniform `pipeline_info/` path across the
> runs' output directories. Execution provenance (task status, resource usage, DAG) is
> available on the linked Platform runs.

---

## Results

### HIV MDDC — bit-identical (branch == dev)

Every per-library and per-replicate peak count and FRiP score matches to full precision.

| Sample | Peaks (branch = dev) | FRiP (branch = dev) |
|--------|----------------------|---------------------|
| HIV_CD86HI_48H_REP1 | 30,438 | 0.216448 |
| HIV_CD86HI_48H_REP2 | 35,854 | 0.230010 |
| MOCK_48H_REP1 | 36,551 | 0.198316 |
| MOCK_48H_REP2 | 51,633 | 0.250963 |
| HIV_CD86HI_48H (replicate) | 69,791 | 0.274689 |
| MOCK_48H (replicate) | 88,666 | 0.281163 |

Consensus peak sets are also identical: **74,895** (merged-library) and **115,880**
(merged-replicate).

### Osmotic SRR — near-identical (heavily subsampled)

| Sample | Branch peaks | Dev peaks | Branch FRiP | Dev FRiP |
|--------|-------------:|----------:|------------:|---------:|
| OSMOTIC_STRESS_T0_REP1 | 8 | 8 | 0.692901 | 0.692901 |
| OSMOTIC_STRESS_T0_REP2 | 16 | 14 | 0.487065 | 0.476560 |
| OSMOTIC_STRESS_T15_REP1 | 4 | 4 | 0.608939 | 0.608939 |
| OSMOTIC_STRESS_T15_REP2 | 9 | 11 | 0.656315 | 0.662069 |
| OSMOTIC_STRESS_T0 (replicate) | 19 | 16 | 0.536935 | 0.517517 |
| OSMOTIC_STRESS_T15 (replicate) | 10 | 11 | 0.712991 | 0.706840 |

Consensus: mLb 19 vs 17, mRp 21 vs 19.

**Interpretation.** On real-depth data (HIV MDDC) the branch reproduces `dev` exactly. On the
toy subset a few peaks sit at the MACS3 significance threshold, so a sub-percent signal shift
flips them in or out; the divergence is **non-systematic** (branch higher on T0_REP2, lower on
T15_REP2) and the higher-signal samples are bit-identical. This is consistent with threshold
jitter in a near-empty subset, not a systematic pipeline behavior change.

**Caveat.** With a single run per arm on the osmotic subset, benign run-to-run marginal jitter
cannot be fully separated from a deterministic low-count difference. The exact HIV identity
makes a systematic, code-driven difference very unlikely.

---

## Samplesheets & input provenance

Two samplesheets are included in `inputs/`, describing the **same four libraries**:

- **`hiv_mddc_public_samplesheet.csv`** — the runnable A/B input. FASTQs are public HTTPS
  URLs on EBI's SRA mirror, so the run needs no private data access. This is what the
  re-verification runs (PR #448 vs #452) consume.
- **`hiv_mddc_private_s3_samplesheet.csv`** — **provenance only, not for launching.** This is
  the exact samplesheet the original real-depth runs (`prickly_cuvier`, `silly_stonebraker`)
  consumed, pointing at the internal us-east-1 bucket (name redacted to `REDACTED-BUCKET`,
  per the sanitization policy below). It documents the true bytes behind the bit-identity
  claim; the public sheet re-points the identical accessions to EBI.

Both sheets map to the same four SRA runs, a two-condition subset of the study below:

| Subset sample        | Rep | Experiment | Run          | Condition in full study            |
|----------------------|-----|------------|--------------|------------------------------------|
| `HIV_CD86HI_48H`     | 1   | SRX5312205 | SRR8508547   | `HIV_GFP_CD86hi_48h` rep 1         |
| `HIV_CD86HI_48H`     | 2   | SRX5312206 | SRR8508548   | `HIV_GFP_CD86hi_48h` rep 2         |
| `MOCK_48H`           | 1   | SRX5312211 | SRR8508553   | `mock_48h` rep 1                   |
| `MOCK_48H`           | 2   | SRX5312212 | SRR8508554   | `mock_48h` rep 2                   |

All four are **paired-end**. This matters for PR #452 (mixed SE/PE per-batch counting): with
an all-PE cohort, #452's endedness split collapses to the single all-PE batch, so its output
must match #448 bit-for-bit — a clean regression check on the split/merge logic.

## Integrity / checksums

`verification/sha256sums.txt` records SHA-256 hashes for every artifact in this bundle (the
four MultiQC reports, `comparison.tsv`, and both samplesheets) — i.e. the integrity hashes of
the already-completed runs' published evidence. Verify from the repo root with:

```bash
sha256sum -c verification/sha256sums.txt      # or: shasum -a 256 -c verification/sha256sums.txt
```

> These hash the **published report artifacts**, not raw pipeline outputs. Byte-level
> checksums of the deterministic pipeline outputs themselves (consensus peak BED/SAF and the
> featureCounts count matrix) will be added alongside the #448/#452 re-run, where they can be
> captured at a uniform `pipeline_info/` + consensus path. BAMs/bigWigs/HTML are intentionally
> excluded from output-level checksums because they embed timestamps, `@PG` lines, and run IDs
> that differ even when results are identical.

## Data provenance

- **HIV MDDC** — ATAC-seq from the published resource *"A Comprehensive Map of the
  Monocyte-Derived Dendritic Cell Transcriptional Network Engaged upon Innate Sensing of
  HIV"*, Johnson, De Veaux et al., *Cell Reports* (2020).
  [PMID 31968263](https://pubmed.ncbi.nlm.nih.gov/31968263/) ·
  doi:[10.1016/j.celrep.2019.12.054](https://doi.org/10.1016/j.celrep.2019.12.054).
  Public data; sample labels (`HIV_CD86HI_48H`, `MOCK_48H`) are study conditions, not
  patient identifiers.
- **Osmotic SRR** — a small public four-sample SRA subset used as a second, independent
  confirmation of the MultiQC deadlock fix.

## Sanitization

These reports were generated on private infrastructure. The internal S3 bucket name has been
redacted to `REDACTED-BUCKET` throughout. No credentials, presigned URLs, or access keys are
present. Numeric QC values are unmodified. The public nf-core reference bucket
(`s3://ngi-igenomes`) is left as-is.
