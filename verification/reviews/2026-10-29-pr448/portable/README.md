# Reproduce the PR448 full-input HIV comparison

This bundle compares reviewed dev **73155d** with proposed fix **a9b588**, for
BWA and Chromap, using all **87,089,251 paired reads** from four human ATAC-seq
libraries. It launches no jobs or downloads automatically. There is one technical
run per biological library; these four runs do not isolate the multi-run library
tag defect. The separate real-library/yeast experiment is a different dataset.

The recorded AWS campaign is now complete: all four arms succeeded, all 324
original scientific artifacts were collected, and actual raw FastQC confirms
87,089,251 pairs in every arm. See `observed/final-summary.md` and
`observed/final-comparison.json` for sanitized final results, and `INTEGRATION.md`
for the distinction between original artifact hashes and distributed public
bytes. This completion record does not stand in for a new reproduction run.

## What is pinned

- Complete Git source archives, full commits and archive SHA-256s are in
  `sources/manifest.json`. `full-proposal.patch` reproduces the complete source
  change; `scientific-fix.patch` contains the three executable/config/environment
  changes only. Pipeline source licensing is preserved in `LICENSE.pipeline`
  and each archive's `LICENSE`.
- Nextflow is **26.04.6**; source configuration pins **nf-schema 2.5.1**. Use a
  supported Java runtime and install/cache the plugin before an offline run.
- `params/` preserves all 41 scientific parameters per arm. `transformations.json`
  records original prepared-payload and original parameter-string hashes, with
  exact normalization of input/output paths and the byte-identical blacklist.
  No private launch config is redistributed.
- `inputs/hiv.csv` lists the eight public ENA HTTPS FASTQs. `ena.json` records
  accessions, MD5, compressed byte count and per-library pair counts. Total
  compressed FASTQ size is 7,198,225,906 bytes. These metadata are recorded ENA
  observations, not a claim that this packaging step downloaded those bytes.
- `references/manifest.json` preserves the original public GRCh38 FASTA/GTF/BWA
  index URI identities. Those large objects were not independently hashed;
  do not mistake a URI for an immutable content pin. The bundled blacklist
  **was** checked byte-for-byte against the recorded immutable source digest.
- Source image declarations are in `sources/container-declarations.json`.
  Observed software versions are retained separately under `observed/`. Source
  container tags, source Singularity blob hashes and resolved task-image digests
  are different evidence. No resolved task digest was invented: the collected
  scientific artifacts did not include a task trace with that field.

## Validate and inspect a local plan

Requires Python 3.9+, Git, Nextflow 26.04.6, a supported Java installation, and a
working Docker/Singularity/Apptainer engine for execution. The resource-heavy full
workflow requires suitable memory, disk and storage; choose limits for your host.
Planning and static validation need no Platform account, workspace, compute
environment, PAT, Docker credentials or cloud job submission.

```sh
python3 reproduce.py validate
python3 reproduce.py plan --run-root ./my-hiv-run
```

The four commands, runtime settings, expanded parameter files and hashes are
written under `my-hiv-run/`. Scientific source is verified against the archives
on each invocation, including an existing extracted tree. Mutable remote nf-core
community configs are disabled using an explicitly recorded runtime-only extra
parameter (`custom_config_base=''`); the 41 scientific parameters are unchanged.

Optional local FASTQ download verifies **both** recorded MD5 and byte count:

```sh
python3 reproduce.py fetch-inputs --input-dir ./hiv-inputs --execute
python3 reproduce.py plan --run-root ./my-hiv-run \
  --samplesheet ./hiv-inputs/hiv.local.csv
```

Public reference S3 URIs remain the defaults. If your resolver cannot access
them anonymously, download/mirror them with your own public-bucket tooling and
provide a JSON object with `fasta`, `gtf` and/or `bwa_index` paths via
`--references refs.json`. The exact replacements are recorded in the new plan;
you are responsible for verifying mirrored reference bytes. Input path changes
via `--samplesheet` likewise describe a new execution and need their own checks.

After inspecting the plan, explicitly execute all arms sequentially:

```sh
python3 reproduce.py launch --run-root ./my-hiv-run --execute
```

Use `--case bwa-unfixed`, `bwa-fixed`, `chromap-unfixed` or `chromap-fixed` for
one arm. Existing attempts are refused without explicit `--resume`, including
failed attempts. Before resuming, prior stdout, receipt, Nextflow logs, trace,
report, timeline, parameters and runtime config move into an attempt-stamped
`cases/CASE/attempts/` directory with file hashes. Session history is copied there
and retained live for the same-arm resume. The new receipt links its predecessor;
other arms' settings and evidence remain untouched. A plain plan also refuses to
overwrite an existing attempt. Never share a work directory across source arms.
Resources default to one
concurrent task, at most 12 CPUs, 200 GB and 48 hours per task; these are portable
execution limits, not recovered historical AWS reservations. Override
`--queue-size`, `--max-cpus`, `--max-memory` or `--max-time` knowingly.

## Your executor and S3-compatible storage

The observed campaign used AWS Batch/Fusion managed through Seqera Platform.
This launcher is a new Nextflow execution: it copies no private Platform launch
configuration, uses no workspace/CE/PAT, and does not claim identical scheduling,
Fusion caching, thread count, BAM tie-breaking or byte-identical outputs.

Local execution is the default. For your own Batch queue or Slurm installation,
provide an explicit Nextflow config and your own executor/storage authentication:

```sh
python3 reproduce.py plan --run-root ./my-hiv-run --executor awsbatch \
  --config ./my-batch.config --work-root s3://YOUR_BUCKET/work \
  --output-root s3://YOUR_BUCKET/results
```

Use the same arguments with `launch --execute` only when ready. For an
S3-compatible provider, configure its endpoint/path-style/region requirements in
your own config, as supported by your Nextflow AWS plugin. Credentials belong in
your normal local/cloud credential mechanism, never in this bundle. A local
executor can also use remote work/output paths with your own storage config.
References, compute queue and storage endpoints must be reachable by workers.

## Compare a new execution

```sh
python3 tools/compare_new_runs.py --run-root ./my-hiv-run --out ./new-comparison
```

This requires actual exit-zero receipts, completed/cached full execution traces,
all expected library metrics, raw FastQC mate counts matching ENA and paired
outputs. It never manufactures Platform IDs or reuses historical workflow
statuses. Missing outputs produce an explicitly incomplete comparison, not PASS.
For remote outputs, mirror each arm to `mirror/CASE/results/` and add
`--collected-root ./mirror`. Preserve the local run-root receipts and traces.
The comparator preserves exact field/cell differences, coordinate/sample joins,
exact-interval Jaccard and merged-basepair Jaccard, without arbitrary tolerances.

## Historical count reproduction and public-byte audit

`observed/` is recorded evidence from the separate AWS campaign, not a new local
run. The four original workflow IDs remain audit metadata only. Historical
matrices come from evidence repository commit **24f0dd**; full hashes/paths are
in `observed/historical-counts/manifest.json`.

```sh
python3 tools/verify_public.py
python3 tools/historical_comparison.py \
  --campaign-root observed/campaign \
  --evidence-repo observed/evidence-repository \
  --comparison-helper tools/observed/strict_compare_campaign_outputs.py \
  --out historical-recomputed.json
```

The staged computation confirms the new BWA fixed matrix exactly matches the
archived old-dev matrix (74,895 regions × 4 libraries = 299,580 exact cells),
and new BWA unfixed exactly matches archived PR448 counts. Old dev versus new
unfixed differs at 6,982 shared cells, with 5,299/5,339 nonshared regions. Archived
old dev is not a fresh run of the immediate pre-448 parent. Matching archived
counts does not establish historical FASTQ byte identity or pipeline-wide
equivalence.

Public byte verification and private launch provenance are separate operations.
`PUBLIC-MANIFEST.json` hashes the actual distributed files and records any
transformations. Sanitized headers or paths can change file hashes even when
coordinate/sample counts remain unchanged. Do not reuse private original-byte
manifests to verify altered public files. The preserved strict helper/reference
are SHA-pinned; the portable helper only changes its reference-file location.
`tools/observed/generate_report.py` and the original campaign audit helper retain
their historical identity contracts: they need full appropriate provenance
envelopes and are not claimed to repeat a private Platform audit on public-only
sanitized payloads. The standalone public/historical commands above are tested.

## Validation scope

Static source/archive/parameter/input/blacklist checks and patch applicability
passed. Four expanded Nextflow configurations parsed using 26.04.6, Docker and
the cached pinned schema plugin; executor/profile/disabled remote config settings
were confirmed. No FASTQ download, new scientific process, container workflow,
cloud launch or publication occurred during staging. Optional full scientific
reexecution remains for the user's machine/environment.
