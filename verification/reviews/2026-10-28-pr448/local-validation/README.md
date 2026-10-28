# Independent local validation evidence

These are retained files from the local Codex verification of candidates raised
by the Co-Scientist source review. They are **not downloads from Co-Scientist**.
The adjacent `coscientist/` directory documents the separate hosted review.

- `aligner/`: two synthetic aligned read pairs representing resequencing runs,
  actual Picard module execution at the historical base/current code, and a
  correction that removes `_Tn` from the library tag. `summary.json` records
  base/current/fixed duplicate-pair counts of 1/0/1 and retained-read counts 2/4/2.
- `trimming/`: 100 synthetic high-quality read pairs, actual Trim Galore module
  executions at the historical base/current code and current with `--no_poly_g`,
  generated FASTQs/trimming reports, and `poly-comparison.json`. The current tool
  removes the 20 leading R2 C bases; base and disabled cases preserve them.

Every selected task has its actual generated shell script saved as `command.txt`,
plus `.command.out`, `.command.err`, and `.exitcode`. The selected task exit codes
are all zero. Run-level stdout is retained as `run.out`. The original fixtures,
final BAMs/FASTQs, metrics, and JSON results are retained; compressed/binary files
are byte-identical to the local originals.

`recorded/` files preserve the original wrappers, configurations, assertions, and
review notes as records of the original environment. They refer to source
checkouts, Docker Colima, and local tool installations that are not bundled here.
They are not promised to run from this publication directory. Recorded review
notes can refer to omitted auxiliary tests or source checkouts and describe the
state when they were written. No downloaded cleanup command was executed.

## Provenance and transformations

`copied-files.tsv` lists every copied file's path relative to the original local
review root, original SHA-256, published SHA-256, byte sizes, and transformations.
It covers the copied evidence, not this generated README or the manifest itself.

Only two literal text-path substitutions were permitted:

1. `/Users/nicholas.deveaux/Dev/tasks-worktrees/atacseq-pr448-review` → `REVIEW_ROOT`.
2. `/Users/nicholas.deveaux/Dev/.agent-nextflow` → `AGENT_NEXTFLOW_HOME`.

The manifest records each applied substitution and its count. No scientific
values, sequences, task exit codes, or tool arguments were changed. Other
recorded environment paths are historical context. Generated shell scripts were
renamed from `.command.sh` to `command.txt` without changing their commands.

The allowlist omits full source clones, dependencies, caches, `.git`,
`.command.env`, `.command.run`, environment dumps, and unnecessary FastQC HTML/ZIP
reports. Common credential/JWT/PAT/AWS-key and signed-URL patterns were checked in
all copied text and decompressed BAM/FASTQ contents; no matches were found.

These small synthetic tests establish the reported local effects. They do not
constitute full-genome workflow executions or measurements of downstream
alignment, peak, or count changes on an instrument dataset.
