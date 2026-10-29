# Independent validation of the proposed Trim Galore fix

Passed against the actual proposed source at `atacseq-pr448-proposed-fix`, based on reviewed dev `73155d`. The harness included the real module and extracted the pipeline's exact `ext.args`, with all referenced parameters set to their literal defaults from that source's `nextflow.config`. Docker Colima and Nextflow 26.04.6 executed fresh tasks; the proposed container was not overridden.

| Case | Actual tool | Pairs retained | R2 leading 20-C sequence |
|---|---|---:|---|
| Pre-#448 baseline | 0.6.10 | 100 | Preserved |
| Unfixed negative control | 2.1.0 | 100 | Removed |
| Proposed default | 2.3.0, `--no_poly_g` | 100 | Preserved |

Both proposed mates' complete FASTQ records—identifiers, sequences and qualities—match the baseline exactly. The negative control still removes 20 terminal G bases from every R1 and 20 leading C bases from every R2, so the fixture continues to distinguish the regression. The actual proposed task script contains `--no_poly_g`; its emitted tool version is `trimgalore=2.3.0`.

Evidence: `comparison.json`, `baseline-comparison.json`, per-case `source-evidence.json`, `source-diff.patch`, `run.out`, `tool-version.txt`, published `outputs/`, and task scripts/logs under `work/`. Source-file SHA-256s are checked again after execution to reject source changes during validation. The archived baseline files were additionally checked against the pinned pre-merge Git blobs.

Re-run with `bash run.sh baseline`, then `bash run.sh proposed ${WORKTREE_ROOT}/atacseq-pr448-proposed-fix`.

Limits: this is a small synthetic paired-end preprocessing regression check. No full pipeline, biological dataset, downstream alignment/peaks/count comparison, SE input or exhaustive parameter matrix was run. No pipeline files were edited and nothing was committed or published.
