# PR448 regression-fix review handoff

Review entrypoint: [source fork at 1d840c](https://github.com/NicoDeVeaux/atacseq-nfcore/tree/1d840c087bd72f227bad1bdf89deccc48a1f0206), branch `fix/pr448-module-regressions`, targeting `nf-core/atacseq:dev` for [issue #473](https://github.com/nf-core/atacseq/issues/473). The fork's versioned [PR-DRAFT.md](https://github.com/NicoDeVeaux/atacseq-nfcore/blob/1d840c087bd72f227bad1bdf89deccc48a1f0206/PR-DRAFT.md) describes the proposed scope. An upstream PR URL and final evidence-release links remain **pending integration**; none is implied here.

This packet maps claims to code, existing runs, counter-controls and limitations. It specifies no score or expected reviewer verdict. A reviewer can accept, qualify or reject individual claims independently. `CLAIMS.json` contains full revision identities, source links, local evidence paths/hashes, run identities and explicit missing integration links. This preparation did not execute tests, scientific tools, workflows or cloud requests. It read the existing evidence and verified the source fork's published commit identity.

## Revision boundaries

| Revision | Role | Evidence boundary |
| --- | --- | --- |
| `4177ea` | Immediate pre-448 parent | Historical baseline for the targeted and yeast core comparisons |
| `a51bee` | Actual PR448 merge | Defines the module-update inventory; not interchangeable with later dev |
| `73155d` | Reviewed current dev / unfixed source | Source used in fresh unfixed HIV and yeast comparisons |
| `a9b588` | Frozen Trim Galore + Chromap-library fix | Source used in the full fixed HIV and yeast runs |
| `604122` | Adds PRESEQ retry-argument correction | Later focused wrapper tests; the earlier full runs do not test this addition |
| `bd5dec` | Adds GFFREAD 0.12.9, registered patch and reviewed snapshots | Later conversion/module tests; the earlier full runs do not test this addition |
| `1d840c` | Current four-fix source plus completed bounded-review documentation | Current review target; not the source of a new all-four-fix full-data campaign |

Full hashes are in the machine map. Source diff assessment should compare the final proposal against `73155d`, while regression attribution should also inspect the relevant `4177ea`/`a51bee` boundary. Merely comparing the final fork with the old parent mixes intended upstream upgrades with the proposed corrections.

Some earlier targeted experiments ran from uncommitted proposal edits or isolated module copies. Their observed checkout HEAD is not presented as a commit containing those edits. Captured file hashes connect the trimming/Picard experiments to `a9b588`; the GFFREAD suite's receipts connect its isolated copy to the later GFFREAD patch. Full workflow runs use the exact frozen commits shown above. These distinctions are recorded in the machine map.

## Four changes and what their tests establish

| Change | Source / existing evidence | Limits and controls |
| --- | --- | --- |
| Trim Galore 2.3.0 plus `--no_poly_g` | Actual module and pipeline arguments; a 100-pair targeted fixture compares pre-448 0.6.10, selected 2.1.0 and proposed defaults. Complete FASTQ records are compared. | Selected 2.1.0 is the triggering negative control. The proposed version alone is insufficient to preserve the old default. The tiny fixture is synthetic; separate real-data experiments assess downstream effects. |
| Chromap shared library ID, distinct technical-run RGIDs | Pipeline RGLB strips only terminal `_Tn`. Actual Picard/merge chains are tested both on small constructed alignments and on identical real aligned inputs from two resequenced libraries. | Unfixed real-input control retains 2,553 / 1,865 extra duplicate pairs. Biological replicates stay separate. HIV has only one technical run per library and cannot isolate this correction. BWA/Bowtie2's similar per-run LB pattern predates #448 and is not changed by this proposal. |
| PRESEQ retry preserves original argv and appends `-defects` | `tests/regressions/preseq_retry.py` runs the actual Nextflow module with an argv-checking stand-in; normal, successful retry and deliberately broken option-loss mutation are checked. | No numerical complexity estimate is validated. `skip_preseq=true` by default; this path is enabled with `--skip_preseq false`. The upstream ignore→retry policy and retry's defect-check suppression are retained, not established scientifically valid by a successful exit. |
| GFFREAD packaged 0.12.9 | Matching module/Conda declarations and registered local patch. Public benign conversion checks coordinates, IDs and runtime. Nine existing module tests pass with reviewed snapshots under strict local `--ci`, nf-test 0.9.5 / Nextflow 26.04.6 / nft-utils 0.0.9. | Public conversion checks do not reproduce historical failure inputs. Those inputs are outside this packet. GTF, FASTA, BED and stub hashes remain unchanged; GFF3 changes are version/command-path comments. Docker amd64 ran; Conda resolution and SIF execution did not. The pipeline's separate helper pin remains 0.0.3; the isolated suite uses upstream helper 0.0.9, which supplies `sanitizeOutput`. |

Read the tests' assertions and recorded task commands, not only their exit summaries. A failure-control that stops being detected changes the meaning of a passing harness.

## Scientific evidence and comparisons

**Full-input human HIV cohort:** Four successful fresh workflows cover BWA/Chromap × unfixed `73155d` / fixed `a9b588`. Each processes the same 87,089,251 pairs across four libraries; these are four workflow executions of one cohort, not four distinct cohorts. Current raw-FastQC mate counts match ENA metadata. Transport-recovery attempts are preserved separately and do not count as successful arms.

The fixed BWA library-consensus matrix matches the archived original-dev matrix at all 74,895 regions and all 299,580 count cells; the fresh unfixed matrix matches the archived PR448 matrix. This is an **archived-matrix comparison**, not a fresh full-input run of the immediate pre-448 parent. Matching accessions/counts do not establish historical FASTQ byte identity. Completion, numerical agreement and biological correctness are separate claims.

**Real resequencing yeast cohort:** Three core workflows compare `4177ea`, `73155d` and `a9b588`. They use four genuine public FASTQ prefixes, 250,000 pairs/run, from two libraries explicitly documented as sequenced twice. All individual-library peak coordinates and all 1,934 consensus regions agree between parent and fix. One of 3,868 count cells differs, 77→76; complete parent/fix equivalence is not asserted. The residual trace identifies an additional new-version Chromap alignment followed by duplicate-representative/NM/orphan-filter effects; the extra alignment's biological correctness and unique upstream-commit cause are not established. Six complementary targeted runs isolate duplicate marking. Optional QC exclusions were equal across core arms, and are listed in the evidence. Raw 101-base reads are unchanged; effective genome sizing uses the supported 100-base bin.

**Same-BAM human MACS3:** Both 3.0.1 and 3.0.4 run on one complete 285,036,036-byte cleaned BAM from fixed-BWA `a9b588`. All 30,438 broadPeak rows/fields and all non-comment XLS rows agree exactly at emitted precision; the 3.0.4 replay also matches archived cloud outputs. GappedPeak fields 7–8 change to zero, while other fields agree. The valid pair uses identical 512-MiB tmpfs; an insufficient 64-MiB attempt is retained as invalid and excluded. Four offline comparison tests detect small numeric changes, coordinate changes despite equal counts, and inappropriate display-field exclusions. This is one paired-end broad/no-control library, not an SE/narrow/control/parameter sweep or a new full-pipeline run.

**Other upgraded tools:** The bounded inventory covers 267 changed module/subworkflow files, 70 components and 16 changed declared dependencies; later history covers 36 shared module paths and seven shared subworkflows. Expected version changes include Chromap mappings/MD tags, BWA SAM metadata, Bowtie2 QC partitioning and MACS display fields. Tested SAMtools, Picard-optical and deepTools boundary candidates were classified as inherited using old/selected binary controls. Absence of a release-note hit is not proof of absence of defects. No broad tool-upgrade equivalence claim is made.

## Reproducible checks

Commands below are **instructions for a future reviewer** and were not run while preparing this packet. `SRC` is a fresh checkout at the mapped final commit; `EVIDENCE` is the local validation root or an integrated downloaded equivalent; `OUT` must be a new writable review directory. Select/copy evidence before commands that write reports. The current evidence mapping uses local paths: a remote grader cannot assume those files exist until the pending integration links are filled.

Source-only checks, from `SRC`:

```sh
git rev-parse HEAD
git diff --check 73155d..1d840c
git diff 73155d..1d840c -- conf/modules.config modules.json modules/nf-core/trimgalore modules/nf-core/preseq/lcextrap modules/nf-core/gffread tests/regressions
git apply -p0 --reverse --check modules/nf-core/preseq/lcextrap/preseq-lcextrap.diff
git apply -p0 --reverse --check modules/nf-core/gffread/gffread.diff
```

Public focused source tests (cached Nextflow and Docker image required as documented):

```sh
python3 "$SRC/tests/regressions/preseq_retry.py" --repo "$SRC" --output "$OUT/preseq"
python3 "$SRC/tests/regressions/gffread_conversion.py" --repo "$SRC" --docker-context colima --output "$OUT/gffread-conversion"
```

Each accepts `--nextflow-jar /path/to/cached/distribution.jar`; the scripts' own help/README specifies their local requirements. Omit `--docker-context colima` when using another Docker setup. The public GFFREAD check is a benign package/conversion check, not the withheld historical-failure test.

Existing evidence comparisons and negative-control tests can be repeated **offline**:

```sh
python3 "$EVIDENCE/behavior-audit/alignment-peak/check.py"
cd "$EVIDENCE/behavior-audit/human-macs"
python3 -B -m unittest -v test_compare.py
cd "$EVIDENCE/real-samples"
python3 -B -m unittest discover -s comparison-tests -p 'test*.py' -v
```

For the nine-test GFFREAD suite, use a fresh isolated copy of the current source module/tests plus the recorded public fixtures and pinned tool/helper. Configure `testsDir="module/tests"`, profile Docker, and `plugins { load "nft-utils@0.0.9" }`; use nf-test 0.9.5 and Nextflow 26.04.6. The recorded invocation is:

```sh
nf-test test --ci --junitxml final.xml --log final.log module/tests/main.nf.test
```

No `--update-snapshot` belongs in that verification command. The mapped `gffread-nftest/{nf-test.config,nextflow.config,provenance.json,final.log,final.xml}` describe the actual environment; normalize fixture paths in a fresh copy, not in the source evidence. Review snapshot differences before treating regenerated snapshots as a test result.

Targeted trimming/Picard and core replay harnesses are under the mapped validation root. Their existing launchers contain local toolchain paths and write run outputs; copy them into a new review directory and adjust only recorded execution paths before explicitly rerunning. Read their READMEs for arguments and existing negative controls. Nothing in this handoff authorizes or automatically launches cloud or paid-model work.

## Known checks that are not all green

Changed-file checks and Nextflow lint passed as recorded. Full nf-core/tools 4.1.0 lint has **13 failures**: five template differences and eight generated-container-config differences. An immutable `a9b588` comparison reproduces the same failure set. Those generated files contain FASTQC bindings only and are not included by the default `nextflow.config`; they are not evidence that the proposed GFFREAD/Trim Galore pins are overridden. Custom inclusion is a different configuration. Baseline debt remains debt, so full lint must not be called passing. A local formatter-bootstrap npm/prek error and separate successful repository formatter check are disclosed in the source draft.

The last full-data workflows still stop at `a9b588`. A passing focused PRESEQ/GFFREAD suite does not relabel them as an all-four-fix full rerun. The final branch needs its own reviewed source/lint status recorded when the review target changes.

## Computation archive and integration status

The complete public yeast control has a deterministic ten-part representation preserving 4,565 files. The joined archive is 431,843,357 bytes, SHA256 prefix `03a1b1`; full identities and member hashes are in the machine map and existing archive manifests. Offline verification checks all parts and every member without scientific execution. The portable bundle's current offline suite contains **18 located test methods**; an original archived report's 20-test statement is historical. Six derived Pearson values differ only at the last bit (maximum 1.45e-15) on offline recomputation; counts/coordinates remain exact. These discrepancies are disclosed rather than rewriting original evidence.

The broader full-HIV output-tree archive/release is still pending final integration. [Reproducibility repository](https://github.com/NicoDeVeaux/atacseq-modules-update-verification) exists; this packet makes no claim that every mapped local artifact is already downloadable there. `integration` in the map has null placeholders for upstream PR, final evidence commit/path and release/assets. Root should fill and verify them before distributing this as a remotely self-contained grader packet.

Checksums establish artifact identity/integrity. They do not establish that a scientific computation or its interpretation is correct. Raw private reasoning, event streams, credentials and historical crash inputs are not included in this handoff.

This is written by GPT-6 (Codex) on Nico DeVeaux's behalf.

Integration note: this distributed copy normalizes private staging paths. `CLAIMS.json` retains original-capture hashes and maps available files to distributed paths. Unmapped entries need the separately described source/archive access. Byte checks in the parent README run on this layout.
