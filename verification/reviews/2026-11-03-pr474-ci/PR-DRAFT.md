Fixes #473.

Restore Trim Galore clipping/poly-G defaults, Chromap library read groups, PRESEQ retry arguments and GFFREAD conversion (0.12.9), with regression tests and reproducible module patches. Also fix the inherited BED-to-SAF start offset, with an exact coordinate regression check.

Evidence: [results and limits](https://github.com/NicoDeVeaux/atacseq-modules-update-verification/blob/19f34e0af4d3619929528b1ba226f95fd40c9a4e/verification/reviews/2026-11-02-pr473-review/docs/pr473-yeast-results.md), [module audit](https://github.com/NicoDeVeaux/atacseq-modules-update-verification/blob/19f34e0af4d3619929528b1ba226f95fd40c9a4e/verification/reviews/2026-11-02-pr473-review/docs/module-update-audit.md), [qualification contract](https://github.com/NicoDeVeaux/atacseq-modules-update-verification/blob/19f34e0af4d3619929528b1ba226f95fd40c9a4e/verification/reviews/2026-11-02-pr473-review/docs/pr473-qualification.md), [full rationale](https://github.com/NicoDeVeaux/atacseq-modules-update-verification/blob/19f34e0af4d3619929528b1ba226f95fd40c9a4e/verification/reviews/2026-11-02-pr473-review/PR-DRAFT.md), [regression reproducers](https://github.com/NicoDeVeaux/atacseq-nfcore/blob/5f74aba1a9942c7e5a29a7658ec47f628269dec3/tests/regressions/README.md), [public outputs and verifier](https://github.com/NicoDeVeaux/atacseq-modules-update-verification/tree/da54c0ee85bcb11ce088e1d974550799fe13edfb/verification/reviews/2026-11-02-pr473-yeast).

CI passes **12/12 tests on Nextflow 25.10.4 and 12/12 on 26.10.5**. [CI diagnosis, count/factor proofs and qualification limits](README.md). Seven snapshot files change only the validated output fingerprints; existing assertions remain intact.

## PR checklist

- [x] Description of changes and reasons.
- [x] Regression tests added.
- [ ] New-tool contribution conventions. N/A: no new tool.
- [ ] Test-datasets PR if needed. N/A: fixtures are inline or existing.
- [x] Code lints: nf-core lint and Nextflow lint pass.
- [x] Full `nextflow run . -profile test,docker --outdir <OUTDIR>` suite passes: [12/12 cases per engine](https://github.com/nf-core/atacseq/actions/runs/41613670857).
- [ ] `docs/usage.md` updated. N/A: no interface change.
- [ ] `docs/output.md` updated. N/A: no output-format change.
- [x] `CHANGELOG.md` updated.
- [ ] `README.md` updated, including citations/contributors. N/A: existing tools and citations.

This is written by an AI agent (model name unavailable) on Nico DeVeaux's behalf.
