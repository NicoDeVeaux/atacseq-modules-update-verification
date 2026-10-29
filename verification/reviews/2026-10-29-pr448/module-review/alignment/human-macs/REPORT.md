Both MACS3 versions produce the same **30,438 broad peaks** from the same full cleaned human library BAM. Every broadPeak field and every non-comment XLS row is identical, including coordinates, signal/pileup, fold enrichment and emitted p/q scores. No numerical tolerance or coordinate-only acceptance was used.

| Comparison | broadPeak | Non-comment XLS | gappedPeak |
|---|---|---|---|
| 3.0.1 vs 3.0.4 | All 30,438 rows/all 9 fields identical | All 30,438 rows/all 9 fields identical | Every row differs only in fields 7–8, which become zero; other fields identical |
| 3.0.4 replay vs archived cloud task | All fields identical | All non-comment rows identical | All 15 fields identical |

The source is completed fixed-BWA workflow `BVYqNpYNcUhEN`, revision `a9b588`, library `HIV_CD86HI_48H_REP1`. The 285,036,036-byte BAM is a complete approved published object. All 34 ranged GETs verified exact Content-Range/Length and the pinned ETag; full input SHA starts `eade69`. Signed URLs and credentials were not persisted. Existing read-only guards revalidated the finished workflow, source, reviewed payload and approved output scope.

The archived cleaned-BAM flagstat reports 5,214,522 total records and 5,138,634 properly paired records. Both MACS runs report 2,569,317 input fragments, matching half the properly paired record count. Full BAM delivery and MACS's reported fragment count are recorded separately.

Scientific argv came from frozen task 101's `.command.sh` and matched an explicit expected argument list. Instrumentation/environment commands were not executed. This is default broad/BAMPE without control: `--keep-dup all --nomodel --broad --broad-cutoff 0.1 --gsize 2701262066 --format BAMPE`, with the archived input/name. Only execution directories and container version differ. The original command and published comparison artifacts match their capture-manifest SHA256 values.

Cached containers ran with networking disabled, read-only except outputs/tmp, 2 CPU/4 GiB limits, and identical 512 MiB tmpfs. Both valid cases exit 0 without traceback/I/O exceptions. Runtime was about 14 and 23 seconds. Exact image identities, argv and limits are in `execution.json`.

The initial harness-imposed 64 MiB tmpfs was insufficient for 3.0.4. That attempt is preserved under `attempt-64MiB/` and excluded: it emitted temporary I/O exceptions despite exit 0. Both versions were repeated with 512 MiB; comparison/tests consume only this valid pair. This does not establish that production encountered that condition.

Evidence is in `comparison.json`, complete observed differences in `differences/`, source receipts in `input-provenance.json` and `archived-source-provenance.json`, and actual outputs/logs in `3.0.1/` and `3.0.4/`. Four offline tests pass, covering exact small-score changes, changed coordinates with equal counts, display-field handling, and the actual human result.

Scope is one full cleaned human paired-end library and this broad/no-control configuration. Emitted-field equality does not inspect internal floating-point differences below output precision. Narrow/SE/control modes, other libraries, parameter sweeps, whole-pipeline or biological equivalence are not established. No cloud jobs, source-fork changes, paid model calls or publication occurred. Retained new data are about 354 MB, below the 1.25 GiB cap.
