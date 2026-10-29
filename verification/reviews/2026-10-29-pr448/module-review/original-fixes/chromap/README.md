# Independent Picard validation of the proposed PR #448 correction

Run `bash run.sh baseline` for the historical pre-PR behavior and, after the patch
has been applied, `bash run.sh proposed`. The proposed default source directory is
`${WORKTREE_ROOT}/atacseq-pr448-proposed-fix`; override it
with `--source /path/to/checkout`. The harness never edits that source directory.

Four tiny synthetic aligned BAMs model two resequencing runs for each of two
biological replicates. All four contain the same mapped read pair coordinates,
but distinct read names. The harness imports actual Picard modules and the full
actual `conf/modules.config`. It extracts the technical-run merging block verbatim
from the selected `workflows/atacseq.nf`, retaining its original pipeline workflow
names so configuration selectors apply. `source-used.json` records source paths,
file hashes, and the exact copied wiring for each run.

Baseline uses the actual historical base modules without RG injection and a
cached Quay mirror of the same Picard 3.1.1 build. Proposed uses its actual
AddOrReplaceReadGroups/MergeSamFiles/MarkDuplicates modules and its own read-group
configuration, with no harness override of read-group arguments.

Assertions require two separate biological-replicate BAMs, one duplicate pair out
of two per replicate, and two retained reads per replicate. For the proposed
source they additionally require distinct RGIDs for the technical runs, a shared
LB and SM within each replicate, disjoint LB values across biological replicates,
and records actually using both expected RGIDs. Results are stored under
`runs/<case>/result.json`; actual task commands and outputs are retained under
that case's work directory.

This models post-Chromap aligned BAMs; it does not run Chromap alignment or the
full ATAC-seq pipeline. It checks cross-run duplicate marking and biological
replicate separation, not downstream peaks/counts on instrument data. Requires
local Docker Colima with the cached Picard/samtools images and the existing
Nextflow 26.10.2 jar; no cloud jobs or remote publication are performed.
