# Original targeted Trim Galore and library-ID controls

This is a frozen public inspection package for the initial two PR448 corrections. It contains the 100-pair synthetic trimming experiment and the constructed two-library/two-run Picard experiment. It is separate from the later genuine-read, full-cohort and optional-module studies. Exporting and checking this package did not execute Nextflow, Docker, a scientific tool, a model or a cloud request.

Run the self-contained offline verifier with Python 3.9+:

```sh
python3 -B verify_public.py
```

It checks the public file inventory/hashes, size limits, excluded-content patterns, captured source receipts, all retained successful task exit codes, complete FASTQ records and the actual small BAM/metrics/read-group outputs. It uses the standard library and does not require source checkouts, containers, a BAM tool, credentials or network access. Hash integrity and these bounded assertions do not prove general pipeline or biological correctness.

## What is included

- `trimming/`: original harness code and receipts; original input FASTQ gzip bytes; all three arms' output FASTQs, trimming reports, task command/stdout/stderr/exit-code evidence, version captures and comparison results. Pre-448 0.6.10 and proposed 2.3.0 plus `--no_poly_g` agree on all 100 paired records. Selected 2.1.0 is the negative control and removes 20 terminal R1 G bases and 20 leading R2 C bases per record.
- `chromap/`: original constructed SAM fixtures, tiny scientific BAMs, harness code, baseline/proposed driver/config/source receipts, task commands/logs/exit codes, published BAMs, actual Picard metrics and captured results. Both biological replicates remain separate; within each, one of two pairs is marked duplicate and two reads remain. Proposed technical-run RGIDs stay distinct while LB/SM are shared within each biological replicate. This experiment starts after alignment; it does not run Chromap mapping.
- `source-capture/`: exact module/config file contents identified by the original receipts, recovered from corresponding Git objects and checked against those receipt hashes. `SOURCE-CAPTURE-MAP.json` relates each receipt to the included files.
- `ARTIFACT-ALIASES.json`: maps normalized historical BAM/metrics locations in the result JSON to the selected published copies. Their original byte hashes agree. This avoids keeping redundant work-directory BAM copies.
- `PUBLIC-MANIFEST.json`: a `files` dictionary recording original/public SHA256 values, sizes, source locators and transformations for every distributed file except the manifest itself. Generated export documentation/checks are marked as generated rather than presented as original evidence.

## Identity and transformations

All original FASTQ gzip bytes are preserved. Fixture SAM bytes are unchanged. Scientific JSON numeric/boolean/null values and object keys are preserved. Local home/worktree/temporary paths and any bucket prefixes are replaced with declared placeholders in textual metadata, scripts and logs. These normalized historical scripts are inspection artifacts; their path placeholders must be deliberately mapped before any future replay. The offline verifier is directly portable.

Small BAMs are retained as valid BGZF BAM files. Only their textual headers have local paths normalized, followed by deterministic BGZF reencoding. Every byte following the BAM text header is unchanged, including reference declarations, read names, sequence/quality data, CIGARs, alignment coordinates, flags and auxiliary fields. The manifest records each original/public header hash and preserved post-header payload hash. The verifier parses the actual retained BAM records and compares their names/flags/RG values against the recorded results.

Original and public hashes have different meanings when a file is transformed. The public hash verifies this distributed file; the original hash identifies the source artifact before declared normalization. A changed public hash is not a claim that the original scientific execution produced sanitized bytes.

The proposed trimming receipt records checkout HEAD `73155d` while the proposal edits were uncommitted. Its captured file hashes, and the proposed Picard source hashes, match files later committed at `a9b588`. The capture map preserves the observed HEAD where available and separately identifies the Git revision supplying matching file bytes. It does not relabel an uncommitted run as execution at a later commit.

Framework/cache/tool binaries, environment files, `.command.run` execution wrappers, framework logs, symlink copies, redundant work outputs and FastQC HTML/ZIP companions are excluded. The companions are unnecessary for these asserted contracts; retaining them would require a separate embedded-content review. No private control-plane or model records are part of this export.

These are deliberately small constructed controls. They establish neither scientific complexity estimates nor real-data downstream peak/count equivalence. Original READMEs retain the historical experimental scope, with paths normalized. The later genuine-read/full-core experiments belong to the separate reproducibility bundle.

This is written by GPT-6 (Codex) on Nico DeVeaux's behalf.
