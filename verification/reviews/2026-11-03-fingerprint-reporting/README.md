# Reproducible fingerprint reporting proposal

[Proposal branch](https://github.com/NicoDeVeaux/atacseq-nfcore/tree/proposal/reproducible-fingerprint-reports) is a separate fork-only experiment based on upstream dev, tracked from [PR #476](https://github.com/nf-core/atacseq/pull/476). It does not change either upstream repair PR.

The branch captures actual controls task commands, raw fingerprint matrices, selected MultiQC configuration/source, observed versions and the two report exports before CI cleanup. A SHA256 manifest distinguishes complete capture from the raw nf-test outcome, including failures in a nonblocking latest-version lane. Artifacts expire after seven days; capture does not waive a failed test.

Control labels now identify their comparison using `::control::`, a delimiter excluded by the real samplesheet checker. A small version-bound MultiQC 1.13 workaround repairs float-keyed numeric TSV serialization without changing the parser's mappings, plot values or explicit YAML/JSON bytes. Separate blocking reporting checks run on Nextflow 25.10.4 and 26.10.5 and feed the existing final CI gate. Reproduction commands are [beside the automated tests](https://github.com/NicoDeVeaux/atacseq-nfcore/blob/proposal/reproducible-fingerprint-reports/tests/regressions/fingerprint_reports.md).

Validated locally:

- Both engines' actual configuration-label probes pass. Each reporting check retains all four fixture curves and 286 exact numeric cells, with identical table bytes after reversing inputs and nine rejected negative controls.
- Thirteen collector tests pass. An action-shell smoke retains nf-test exits 0 and 23. Actual full-controls capture verifies all 25 retained files and identifies the failed snapshot result separately from complete capture.
- The original-label-format candidate completed all 253 tasks under Linux Nextflow 25.10.4. A final-source bridge reran its four real fingerprint producers and MultiQC successfully, preserving all eight curves and 782 numeric values. Raw bin rows reorder between producer executions, but their complete row multisets and quality numeric fields agree.
- Pre-commit formatting, whitespace and Nextflow lint checks pass. Standalone lint reports zero errors and the three existing warnings.

Qualification remains open. The first full Linux 26.10.5 driver stalled after 26 completed tasks, before reporting; the last observed sort exited 0 and the JVM did not respond to one diagnostic attach. It was stopped with its data retained. This establishes neither a full pass nor a proven product defect. A separately retained host-native orchestration attempt is checkpointed for follow-up. Neither missing historical CI raw inputs nor the old hash discrepancy has been reconstructed exactly.

[Two candidate controls replacements](FINGERPRINT-CONTROLS-CANDIDATES.json) are **unapplied**. Validate the final source in complete controls runs on both engines, check all eight curves and exact numeric exports in both input orders, then apply only the justified report expectations and rerun without snapshot-update mode. The serialization repair also affects no-control report TSVs, so assess those profiles before declaring the complete pipeline matrix green. Do not import unrelated featureCounts executable-header differences from local emulation. Quality metrics are currently emitted by deepTools but are not staged into MultiQC by the existing workflow; this proposal does not expand that routing.

All local validation data is retained until issue #473 is resolved. The detailed local checkpoint is `/private/tmp/atacseq-reporting-proposal-evidence-20261103`; the code worktree is `/private/tmp/atacseq-reporting-proposal-20261103`.

This is written by an AI agent (model name unavailable) on Nico DeVeaux’s behalf.
