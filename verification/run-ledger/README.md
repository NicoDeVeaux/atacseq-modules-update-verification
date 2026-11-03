# ATAC-seq run and verification ledger

Start here to find what ran, which exact source and inputs it used, what was verified, and where the evidence lives. This compact ledger is based on supporting-repository commit `0b9140` plus the hash-bound execution receipts listed in [EVIDENCE.json](EVIDENCE.json). Full digests are in JSON; six-character prefixes below are display labels.

```sh
python3 verify.py
python3 lookup.py a9b588
python3 lookup.py --result 299580
python3 lookup.py 826e7e --json
```

| Campaign | Executed source | Execution and verification |
|---|---|---|
| Four HIV workflows | `73155d` versus `a9b588` | Four successful full BWA/Chromap arms, 87,089,251 input pairs each. Fixed BWA restores all 299,580 archived count values. Fixed/unfixed peaks and counts differ; general scientific equivalence is not claimed. All four workflow IDs are retained in [RUNS.json](RUNS.json). |
| Real technical resequencing | `4177ea`, `73155d`, `a9b588` | Three core workflows succeeded. On identical alignments, fixed/pre-448 duplicate behavior agrees; unfixed retains 2,553/1,865 extra pairs. Fixed restores 1,934 consensus coordinates; one of 3,868 full-workflow count cells differs. |
| Native GTF/GFF3 and PRESEQ | `4def83` | Both scientific arms succeeded on NF26.04.6. Checker passes; all 3,868 counts and both 10,000-row PRESEQ curves agree. Default GFFREAD omits 91 transposable-element transcripts. The original `.gff3.gz` filename attempt failed before scientific tasks; the accepted alias has identical bytes. No natural PRESEQ retry occurred. |
| Historical combined #474 CI/stage campaign | Runtime `ff886e`; CI `4b26f7` | Runtime CI had seven snapshot-only failures per engine; reviewed expectations then passed 12/12 tests on each engine. Later split head `f28734` has a separate successful GitHub run 41644797269; its raw nf-test summaries are not reverified here. BWA/Chromap count interventions, trimming and MACS controls have separate bounded assertions. Six historical scaling-factor causes remain unknown. |
| Full BWA count/SAF intervention | `a9b588`, `ef206a`, split `f28734` | Legacy and post-split #474 stages restore all 299,580 archived values. Start+1 changes 2,280 cells across 2,223 regions, total −2,293, and fails literal old-count equality. A real boundary read changes 1→0. Stage-script hashes and the pinned Subread image identify the local execution; pipeline commits identify annotation origin. These are counting stages, with no new alignment/full workflow. |
| Standalone #476 final CI | Published `9a255c`; checkout `69a3dd` | Native CI run 41666190365 passes 12/12 actual tests on NF25.10.4 and 12/12 on NF26.10.5: seven real tests and five stub tests per engine. Checkout tree matches reviewed source. The two controls-report baseline changes do not repair MultiQC. |
| Fingerprint reporting proposal | Base `73155d`; literal trees `a22dc3` / `55a642` | Literal NF25 uses helper `723bf5`; full NF26 uses `532bfb`, followed by actual final-helper `723bf5` report replays. All eight series/782 values and both exports agree across five contexts. Default preserves six curves/473 values. No native CI or nf-test assertion rerun is claimed for these local replays. |

The fingerprint proposal's later published commit is `826e7e`. It is recorded separately from the exact source copies that executed. Eleven focused negative controls per engine and 18 independent naming/parser checks pass. A header-only counterfactual reproduces both old report hash pairs, while historical CI raw files and actual ordering remain unknown. Bowtie2, Chromap, STAR and skip-trimming still have no qualified final numeric-report candidates; skip-consensus is source-derived rather than independently executed.

The NF25 reporting workflow recovered one plotHeatmap exit 139 through its unchanged retry policy; its cause is unknown. An earlier emulated NF26 driver stalled before reporting. STAR/Chromap diagnostics with exit 143 are recorded as failures. Legacy cache records without an execution-source binding stay `UNKNOWN`; current checkout HEAD cannot supply that missing history.

`PASS`, `FAIL`, `NOT_RUN` and `UNKNOWN` apply to individual assertions. `NOT_RUN` means unexercised; `UNKNOWN` means an unresolved observation or identity. Execution success, scientific checks, nf-test results and native CI are separate fields in [RUNS.json](RUNS.json). [SOURCE-MAPS.json](SOURCE-MAPS.json) preserves complete frozen source-file hashes; [INPUTS.json](INPUTS.json) pins known data identities and reference gaps; [CONTAINERS.json](CONTAINERS.json) preserves observed digests, including 185 native yeast task bindings. Source declarations are never promoted to observed image identities.

Archive availability is explicit in [ARCHIVES.json](ARCHIVES.json). Public material includes the split resequencing/native-yeast bundles, the complete selected count/SAF tables and witnesses, and the compact fingerprint data package. Many work-cache intermediates and the four full-cohort recount BAMs have no public copy in those packages. This ledger preserves identities and observed results; it does not claim every output is remotely downloadable or authorize deletion. Cleanup decisions and removal receipts remain separate.

The [legacy task-source capsule](legacy-cache/README.md) preserves 4,464 observed cache records, 1,901 distinct script hashes and their recorded exits. It includes copied caches and synthetic controls. These observations have unknown historical source/execution bindings and do not establish scientific PASS.

[HASH-INDEX.json](HASH-INDEX.json) links full digests to exact evidence JSON fields and campaign IDs. Unknown reference/image hashes remain null with an explanation. Large original logs and runtime caches are represented by recorded hashes and selected verification receipts rather than copied into this ledger.

This is written by an AI agent (model name unavailable) on Nico DeVeaux's behalf.
