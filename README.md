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

### Revision provenance
The branch A/B runs were executed at `52836f0`. That commit was later **metadata-only
rewritten** (author change) to `0116142`, which is **tree-identical** to `52836f0` — so the
code that was tested is exactly the code in the PR at that point. The only commit after it,
`b8f1b53`, is **whitespace-only** (test snapshots), with no runtime effect. `52836f0` is
therefore not present in PR history by SHA; look for `0116142`.

---

## What's here

```
verification/
├── comparison.tsv              # machine-readable A/B peak-count + FRiP table (all runs)
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
