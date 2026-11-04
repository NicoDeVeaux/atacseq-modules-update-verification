# Native fingerprint report qualification

Final source `e8aafb` passes **24/24 ordinary assertions**: seven real and five stub cases on each of NF25.10.4 and NF26.10.5. All fourteen actual native report qualification lanes and both contract jobs pass. [Final verification](FINAL-VERIFICATION.json) binds the source, run, captures and exact export hashes.

This report separates actual native job/nf-test results from the fingerprint-report semantic checks. Each attempt remains visible. Admitting candidate hashes does not rewrite the earlier recorded test outcomes.

| Attempt | Source | Native profile jobs | Semantic passes |
|---|---|---|---|
| [41777278460-attempt-1](https://github.com/NicoDeVeaux/atacseq-nfcore/actions/runs/41777278460) | `70e87c` | 0/14 successful | 0/14 |
| [41782995985-attempt-1](https://github.com/NicoDeVeaux/atacseq-nfcore/actions/runs/41782995985) | `e8aafb` | 14/14 successful | 14/14 |

Ordinary nf-test observations:

- 41777278460-attempt-1, NF25.10.4: 8/12 expected tests recorded as passing; 7 real and 5 stub records. Exact expected-name coverage: true.
- 41777278460-attempt-1, NF26.10.5: 8/12 expected tests recorded as passing; 7 real and 5 stub records. Exact expected-name coverage: true.
- 41782995985-attempt-1, NF25.10.4: 12/12 expected tests recorded as passing; 7 real and 5 stub records. Exact expected-name coverage: true.
- 41782995985-attempt-1, NF26.10.5: 12/12 expected tests recorded as passing; 7 real and 5 stub records. Exact expected-name coverage: true.

[NATIVE-ATTEMPTS.json](NATIVE-ATTEMPTS.json) retains real/stub TAP observations, per-job outcomes and raw capsule identities. [CANDIDATE-ADMISSION.json](CANDIDATE-ADMISSION.json) requires both engines to qualify identical captured exports; no-control numeric plots must retain their existing snapshot MD5. Only exact declared report expectations are candidates. No snapshot is edited here.

[SOURCE-MAPS.json](SOURCE-MAPS.json), [INPUT-BINDINGS.json](INPUT-BINDINGS.json) and [CONTAINER-BINDINGS.json](CONTAINER-BINDINGS.json) bind selected source files, actual raw matrices and observed reporting task references. Native downloaded FASTQ/reference hashes remain unknown. Prior public immutable fixture identities remain historical evidence rather than an assertion about these downloads.

The qualification scope is six no-control curves or eight treatment/control curves, exact original-parser numeric values, unique labels, numeric TSV cells, actual workflow export equality and forward/reverse order invariance. Focused negative controls are reported separately from the real profile cases. Unsupported or incomplete contexts do not qualify.

Earlier [local reporting evidence](../2026-11-03-fingerprint-reporting/README.md) and the [canonical run ledger](../../run-ledger/README.md) remain available. This compact report retains selected reporting evidence, not every pipeline output/cache. It neither authorizes deletion nor claims full scientific output archives are public.

The original run had 16 ordinary test passes and eight real count-expectation failures; all stubs passed. Its fourteen native capture/qualification gates remain PARTIAL/FAIL. The [separate local posthoc bridge](posthoc/SUMMARY.json) qualifies unchanged native output payloads across all fourteen lanes and is never promoted to an original native PASS. The [four-hash admission](admission/SNAPSHOT-ADMISSION.json) changes only the remaining counts expectations; all seven plots, the other three counts expectations and the reporting application payload are unchanged.

[Current controller identities](CURRENT-CONTROLLERS.json) distinguish executed application bytes from replay/controller code. [Cache context](COST-CONTEXT.json) records the implicit setup cache at 16,753,790 bytes within the free 10 GB quota. Standard public Ubuntu runners were used; no paid compute or artifact upload was required.

Final effective report configurations and the two fingerprint exports agree with the initial native outputs. All [80 raw matrices](RAW-ORDER-COMPARISON.json) differ only in row order: headers and multisets of complete rows, including treatment/control pairs, are identical. Literal raw-byte equality remains false in the final receipt. Each final lane independently qualifies its actual captured raw vectors against the original parser.

This is written by an AI agent (model name unavailable) on Nico DeVeaux's behalf.
