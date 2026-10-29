This package contains the frozen PR448 module/version scan and selected public-data GFFREAD validation evidence. It provides auditable inputs, source identities, classifications, test records and checksums for independent review.

Run `python3 -B verify.py` from this directory. It performs offline content checks only. `PUBLIC-MANIFEST.json` is the complete file allowlist and excludes itself. The intended integration location is `module-review/modules`.

| Evidence | Coverage and meaning |
|---|---|
| `module-version-audit/` | All 267 changed files assigned to 70 components; all 16 changed declared dependencies scanned; 36 shared-module and 7 shared-subworkflow histories |
| `annotation-matrix/` | Exactly six files from the pre-existing public allowlist: a summary and benign fixed-version conversion smoke fixture/results |
| `gffread-suite/` | Existing nine-test module suite, public SARS-CoV-2 inputs, pinned module/config, strict CI result, reviewed old/raw snapshots and safe run output |
| `source-fork/` | Selected immutable source-fork files, including the registered local module patch, normalized snapshot and unchanged pipeline nf-test config |
| `VALIDATION.json`, `SOURCE-MAP.json` | Exact source pins, computed coverage, original-to-public hash mapping, transformations and validation scope |

The scan compares actual first parent `4177ea` with merge `a51bee`. It records source-declared versions and literal image references separately; it does not infer the contents of opaque containers. Upstream histories are pinned in their JSON files. The dated scan documents retain their original applicability classifications and then-current campaign-status wording. The later GFFREAD follow-up and suite proof are separate evidence, rather than a silent rewrite of the historical scan.

The nine existing GFFREAD tests passed a strict `--ci` run with nf-test 0.9.5, Nextflow 26.04.6, the fixed 0.12.9 package container and an isolated `nft-utils@0.0.9` helper. That helper matches the module's recorded upstream source. The source fork's pipeline helper remains `nft-utils@0.0.3`, and its pipeline config ignores vendored module tests. The isolated suite result is therefore not a claim that the pipeline's default test configuration ran these nine tests.

The strict run used the raw nf-test snapshot. The source fork subsequently normalized its JSON whitespace/layout. Both snapshots are included; their parsed JSON is identical. Tested module main bytes also match the pinned source-fork module. `VALIDATION.json` records full hashes and the exact source-fork commit. The GFF3 snapshot's changed output hash is explained by its version and command-path comments; restoring those comments reproduces the prior hash exactly. GTF, FASTA, BED and stub output hashes were unchanged. The pre/post-update review records and snapshot diff preserve that distinction.

All selected files are text. Personal filesystem paths and terminal color escapes were normalized where present; the fixture-data config now uses `${projectDir}/data/`. Each public manifest row retains the original SHA256, public SHA256, byte sizes and transformations. Nested historical provenance hashes still describe the captured original bytes, including some tool/cache objects intentionally omitted from this package; they are not assertions about normalized public bytes. Public-byte verification uses `PUBLIC-MANIFEST.json`.

The six annotation files are the complete approved subset. Historical GFF failure inputs/scripts, binary tool archives, temporary caches and private Co-Scientist material are excluded. This package does not establish that all upgraded tools are behavior-preserving or that the pipeline is free of defects. It does not include the separate full-data cohort comparison. No scientific reruns, cloud jobs, paid model calls or publication were performed while preparing it.

The historical builder scripts in the scan describe its computation and require the exact pipeline source checkout identified there. Replaying the GFFREAD suite requires the recorded external tools/container and user-chosen local Docker configuration; no replay runs automatically. The supplied verifier checks the exported records and inputs without executing the pipeline or external tools.
