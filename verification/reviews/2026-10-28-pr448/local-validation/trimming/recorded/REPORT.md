# PR #448: Trim Galore correctness check

Confirmed scientific preprocessing regression: the 0.6.10 → 2.1.0 upgrade enables poly-G autodetection without an explicit pipeline choice. In the pinned 2.1.0 implementation, this also trims poly-C from the **5′ end of R2**, which upstream acknowledges is the wrong end for the two-colour sequencing artifact. High-quality biological R2 bases can therefore be removed silently.

The pipeline's current `modules/nf-core/trimgalore/main.nf:7` pins the affected container; `conf/modules.config:154` supplies no `--no_poly_g` opt-out. The source and arguments remain unchanged from the PR merge to reviewed `dev` (73155d).

Reproduce with `bash run-poly.sh`. It executes the actual module from the pre-merge base and current `dev`, with `ext.args` extracted verbatim from the corresponding pipeline configuration. Trimming/clipping parameters are at their defaults. The old container is obtained from the Quay mirror of the same pinned bioconda build. These are real executions, not stub commands.

The fixture has 100 high-quality paired reads, R1 with 20 terminal G bases, R2 with 20 leading C bases, and no adapter sequence. No `--poly_g` flag is supplied.

| Actual module/tool | R2 5′ C bases retained | Pairs retained |
|---|---:|---:|
| Base / 0.6.10 | 20 | 100 |
| Current / 2.1.0 default | 0 | 100 |
| Current / 2.1.0 + `--no_poly_g` | 20 | 100 |

All three Nextflow runs exit 0. The workaround restores the exact base FASTQ sequences in both mates. `poly-comparison.json` preserves the actual sequences; each `poly-nf-*/run.out`, `outputs/` and task `.command.sh`/`.command.err` preserves execution evidence. The fixture establishes sequence loss; downstream alignment/peak/count effects have not been measured and should be described as a risk.

Pinned upstream tool source is cloned under `trim-galore-v2.1.0/`, commit recorded in its Git metadata and also announced by the actual 2.1.0 binary. `src/main.rs:333` enables autodetection when the count exceeds `max(reads_scanned/10000,10)`. `src/trimmer.rs:219` sets `revcomp = is_r2`, and line 224 clips the R2 5′ end. [Upstream's 2.3.0 changelog](https://github.com/FelixKrueger/TrimGalore/blob/master/CHANGELOG.md#version-230-release-on-27-june-2026) explicitly identifies and fixes this wrong-end handling. A safe compatibility fix for this PR is to disable the new autodetection with `--no_poly_g`, with any new trimming behavior introduced as a deliberate option. Upgrading the tool fixes the wrong-end implementation but still changes default preprocessing relative to 0.6.x.

Issue searches using `poly`, `"Trim Galore"`, and `trimgalore` found no matching atacseq issue in returned results; a modules search for `"poly_g"` also found none. Full search terms and result titles are in `issue-searches.json`. This is a known upstream tool defect; its propagation through PR #448 is independently reproduced here. Nothing has been published.

Separately refuted: Trim Galore 2.1.0's report format does **not** break the read-count parser in the ordinary SE/PE cases tested. `bash run.sh` includes the real current subworkflow, trims 12-read fixtures to 12 or 4 reads, and verifies that threshold 8 retains exactly the two 12-read samples. The variable renaming in the subworkflow fixes the old missing-log guard/fallback; it is not the cause of the confirmed regression.

Limits: no full genome pipeline, instrument dataset, cloud job, or peak/count comparison was run. Generic report parsing and poly-G sequence changes were tested on small synthetic inputs using actual tool containers under Docker Colima, with Nextflow 26.04.6.
