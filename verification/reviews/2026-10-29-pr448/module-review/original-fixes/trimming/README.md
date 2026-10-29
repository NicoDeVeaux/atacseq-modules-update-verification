Independent tiny trimming comparison; no pipeline source is edited.

Run `bash run.sh baseline` to execute the actual pre-448 Trim Galore 0.6.10 module and the unfixed 2.1.0 negative control. After the proposed patch is ready, run `bash run.sh proposed /absolute/path/to/proposed/atacseq`.

The harness extracts the selected source's actual TRIMGALORE `ext.args` and each referenced parameter's literal default. It includes the real module, selects Docker Colima and executes fresh tasks. Only the old base container repository is mapped to the Quay mirror of its identical pinned bioconda build. Per-case source paths, commit when available, source-file SHA-256s, exact arguments and defaults are saved in `source-evidence.json`. Task scripts/logs and published tool outputs remain under each case directory.

The same synthetic 100-pair fixture has high-quality R1 terminal 20-G and R2 leading 20-C sequences. Assertions compare complete FASTQ records (identifiers, sequence and quality), verify 100 pairs retained, check actual proposed tool version 2.3.0 and inspect its executed task for `--no_poly_g`. The negative control must continue to reproduce the original wrong-end trimming.

This establishes preservation of the pre-448 default on the triggering fixture. It does not assess biological datasets, downstream mapping/peaks/counts, every flag combination, or optional poly-G behavior.
