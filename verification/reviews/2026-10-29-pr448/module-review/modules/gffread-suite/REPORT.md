All nine existing GFFREAD module tests pass against the exact 0.12.9 package container with nf-test 0.9.5, Nextflow 26.04.6 and the upstream module's nft-utils 0.0.9 helper. The final run used `--ci` without snapshot updates:9 tests,0 failures,0 skips.

Candidate: `candidate/main.nf.test.snap`; review: `snapshot.diff`, `pre-update-review.json`, `post-update-review.json`; full identities: `provenance.json`. The original module test script is unchanged. Main/environment pins changed only in this isolated copy.

All eight snapshot mismatches were reviewed before generating this candidate. GTF, FASTA, BED and stub output hashes are unchanged. GFF 3's hash differs solely because the two comment lines identify 0.12.9 and its packaged command path; restoring those comments reproduces the old snapshot MD 5 exactly. Snapshot content changes are restricted to version strings and that GFF 3 hash; metadata records the actual rerun timestamps and Nextflow version.

The pipeline's old nft-utils 0.0.3 helper lacks `sanitizeOutput`; the exact upstream module source uses 0.0.9. Early tooling attempts and one discarded isolated update are recorded in `attempts.json`; the original snapshot was restored before the reviewed baseline. No discarded snapshot is proposed.

Nextflow task containers had network disabled and used the already cached fixed image. Public SARS-CoV-2 fixture bytes were downloaded outside task containers and hashed. No historical crash inputs, canonical source changes, scientific cloud jobs or publication occurred. This module suite does not establish whole-pipeline correctness or replace the separate annotation score-field checks.
