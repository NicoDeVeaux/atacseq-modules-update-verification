# PR448 module fixes: real-library validation

**The separate Chromap library-ID correction passes. All three core workflow runs completed and passed their output gates.**

The correction is already published on [fix/pr448-module-regressions](https://github.com/NicoDeVeaux/atacseq-nfcore/tree/fix/pr448-module-regressions) at `a9b588`. Technical runs keep distinct RGIDs and share RGLB within a biological library; Trim Galore does not supply this correction.

Co-Scientist found PRJNA844120. The primary GEO records for [d28](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM6208857) and [d28p](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM6208858) each explicitly document sequencing the same library twice. Inputs are SRR19479022/23 and SRR19479020/21, respectively. The two libraries remain separate.

Each input contains the first 250,000 genuine paired records, 1,000,000 pairs total. The reference and matched annotation are sacCer3. No input record was duplicated or fabricated.

## Core workflow comparison

| Library | Pre-448 peaks | 448/dev peaks | Fixed peaks |
|---|---:|---:|---:|
| D28_REP1 | 1635 | 1406 | 1635 |
| D28P_REP1 | 1431 | 1436 | 1431 |

All individual-library peak coordinates and all **1,934 consensus regions** match pre-448 exactly. Unfixed dev produces 1,800 consensus regions. Peak scores and metadata are compared separately and are not all identical.

**One of 3,868 count-matrix cells differs:** D28P at chrIV:42072–43938 is 77 before the PR and 76 on the fix. Every D28 count agrees. Unfixed dev has 663 changed cells on shared intervals, plus a different consensus-region set.

| Library | Pre-448 cleaned reads | 448/dev cleaned reads | Fixed cleaned reads |
|---|---:|---:|---:|
| D28_REP1 | 564934 | 569486 | 564934 |
| D28P_REP1 | 567510 | 570996 | 567508 |

## Isolated library-ID test

Giving all three duplicate-marking paths identical real alignments makes pre-448 and fixed outputs agree exactly in retained read names, fragment coordinates and duplicate counts. Unfixed dev retains **2,553 extra duplicate pairs for D28 and 1,865 for D28P**. RGIDs stay distinct and library IDs correctly join only technical runs from the same library.

## Residual one-count trace

The selected raw and trimmed FASTQ records are identical between base and fix. A fixed-only Chromap alignment (`SRR19479021.241454`) changes which duplicate representative is retained; its high-mismatch mate then fails the identical NM filter, and orphan removal drops the remaining mate. The original pair (`SRR19479021.220045`) has already been marked duplicate and removed. This explains the one-pair loss and the 77→76 count. The extra alignment's biological correctness and attribution to a particular upstream change remain unestablished. [Extracted records and commands](residual-one-count/REPORT.md).

## Validation conditions

- Source pins: pre-448 `4177ea`, reviewed dev `73155d`, fix `a9b588`; tracked sources are unchanged. Baseline archive bytes were checked against its Git objects.
- All scientific parameters match except output directories. The supported 100-bp genome-sizing bin is used for actual 101-bp reads; read records are unchanged. Every MACS3 command uses effective genome size 11,777,680.
- Actual main.nf entrypoints execute alignment, duplicate marking, filtering, bigWigs, peak calling, annotation, FRiP, consensus featureCounts and MultiQC. Both libraries' nonempty peaks, cleaned BAMs and count columns are required by completion gates.
- Optional deepTools, ATAQV, PRESEQ, DESeq2 QC, Picard CollectMultipleMetrics and R peak-QC plots are disabled equally. Legacy optional-QC runtime failures and all retries are preserved. These subsets support no biological differential inference.
- Six targeted Nextflow experiments and three core workflows succeeded. Twenty comparison/parser tests passed. Completion and numeric equivalence are separate checks.
- Co-Scientist's broad search was stopped after useful candidates were recovered. Selected actual tool outputs and independent primary metadata are retained; no final research narrative or successful sandbox-file download is claimed.

## Evidence

- [Full output comparison](full-core-comparison/COMPARISON.md) and [machine-readable differences](full-core-comparison/comparison.json)
- [Core completion gates](full-core/completion-check.json), [frozen campaign and runtime corrections](full-core/campaign.json)
- [Identical-alignment analysis](analysis/shared/REPORT.md), [raw-read analysis](analysis/raw/REPORT.md), [library-ID validation gates](validation-result.json)
- [Input selection and checksums](selected-inputs.json), [primary queries](primary-metadata/queries.json), [actual Co-Scientist tool evidence](primary-metadata/coscientist-search-evidence.json)
- Full task commands, trace, reports, metrics, BAMs and scientific outputs are under `full-core/cases/{base,unfixed,fixed}`.
