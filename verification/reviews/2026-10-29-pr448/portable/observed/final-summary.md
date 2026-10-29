# Full-input HIV ATAC-seq comparison

**FINAL**. Generated 2026-10-29T08:00:38.568097+00:00; comparison observed 2026-10-29T08:00:23.762139+00:00.

Reviewed dev pin [73155d](https://github.com/nf-core/atacseq/commit/73155d2b59d37f521e3f00228d559031d2e7847f) versus proposed fix [a9b588](https://github.com/NicoDeVeaux/atacseq-nfcore/commit/a9b588235e4a1ceb3c8838acad430628c5737c86). This is a fresh matched-source comparison, not a pre-448 replay or scientific PASS.

**87,089,251 input pairs, four biological libraries, one technical run per library.** These runs do not isolate the cross-technical-run Chromap library-ID correction.

| Aligner / arm | Workflow | Physical name | Status | Collection complete | Verified files |
|---|---|---|---|---|---:|
| bwa / unfixed | miH78tIWtzQMy | pr448-hiv-bwa-unfixed-a9b588 | SUCCEEDED | True | 81 |
| bwa / fixed | BVYqNpYNcUhEN | pr448-hiv-bwa-fixed-a9b588 | SUCCEEDED | True | 81 |
| chromap / unfixed | 6n2TeKZ3HxTua | pr448-hiv-chromap-unfixed-a9b588_r2 | SUCCEEDED | True | 81 |
| chromap / fixed | 2DOXAsX9V2FbkY | pr448-hiv-chromap-fixed-a9b588_r2 | SUCCEEDED | True | 81 |

## Outcome at a glance

| Aligner | Cleaned reads unfixed | Cleaned reads fixed | Δ cleaned reads | Library consensus exact Jaccard | Covered-base Jaccard | Changed shared count cells |
|---|---:|---:|---:|---:|---:|---:|
| BWA | 26,700,300 | 26,695,736 | -4564 | 0.8674128175087868 | 0.9928887420273258 | 6,982 |
| CHROMAP | 26,101,486 | 26,106,762 | +5276 | 0.8723041709053917 | 0.9940572916380384 | 8,065 |

High covered-base overlap does not imply identical intervals or counts. Changed cells refer only to exact shared coordinates; nonshared intervals are reported separately.

## Input identity and full-input verification

| Library | ENA run | ENA pairs | Archived raw reads per mate |
|---|---|---:|---:|
| HIV_CD86HI_48H_REP1 | [SRR8508547](https://www.ebi.ac.uk/ena/browser/view/SRR8508547) | 21,260,206 | 21,260,206 |
| HIV_CD86HI_48H_REP2 | [SRR8508548](https://www.ebi.ac.uk/ena/browser/view/SRR8508548) | 20,649,365 | 20,649,365 |
| MOCK_48H_REP1 | [SRR8508553](https://www.ebi.ac.uk/ena/browser/view/SRR8508553) | 21,344,854 | 21,344,854 |
| MOCK_48H_REP2 | [SRR8508554](https://www.ebi.ac.uk/ena/browser/view/SRR8508554) | 23,834,826 | 23,834,826 |

Actual current-arm MultiQC is selected by the explicit **LIB: FastQC (raw)** namespace. Both mates of every library must exactly match ENA. Missing, ambiguous or mismatched counts block a final report.

| Aligner / arm | Actual R1 / R2 counts per library | Total input pairs |
|---|---|---:|
| bwa / unfixed | HIV_CD86HI_48H_REP1: 21,260,206 / 21,260,206; HIV_CD86HI_48H_REP2: 20,649,365 / 20,649,365; MOCK_48H_REP1: 21,344,854 / 21,344,854; MOCK_48H_REP2: 23,834,826 / 23,834,826 | 87,089,251 |
| bwa / fixed | HIV_CD86HI_48H_REP1: 21,260,206 / 21,260,206; HIV_CD86HI_48H_REP2: 20,649,365 / 20,649,365; MOCK_48H_REP1: 21,344,854 / 21,344,854; MOCK_48H_REP2: 23,834,826 / 23,834,826 | 87,089,251 |
| chromap / unfixed | HIV_CD86HI_48H_REP1: 21,260,206 / 21,260,206; HIV_CD86HI_48H_REP2: 20,649,365 / 20,649,365; MOCK_48H_REP1: 21,344,854 / 21,344,854; MOCK_48H_REP2: 23,834,826 / 23,834,826 | 87,089,251 |
| chromap / fixed | HIV_CD86HI_48H_REP1: 21,260,206 / 21,260,206; HIV_CD86HI_48H_REP2: 20,649,365 / 20,649,365; MOCK_48H_REP1: 21,344,854 / 21,344,854; MOCK_48H_REP2: 23,834,826 / 23,834,826 | 87,089,251 |

Archived counts/accessions agree with ENA. Matching counts do not establish byte identity between historical stored FASTQs and public ENA objects. Metadata MD5s and response/report hashes remain in `hiv-input-provenance.json`. No historical byte-for-byte replay is asserted.

## Matched settings and ENA recovery

Chromap initial attempts encountered ENA transport/remote-existence failures. Campaign records preserve source-identical, same-arm resumes and unchanged scientific inputs/parameters; foreign-file transfer retries/concurrency changed to 8/2. Physical recovery names end `_r2`; logical keys and source pins stay stable. Initial failed attempts do not count as successful comparison arms.
- chromap / unfixed: initial [48WxHkBBQLwjxZ]() → current 6n2TeKZ3HxTua.
- chromap / fixed: initial [52m3J1jROxpico]() → current 2DOXAsX9V2FbkY.

Nextflow 26.04.6. The old blacklist checkout path was replaced across all arms by an immutable URL for verified identical blacklist bytes.

| Aligner | Parameters per arm | Only parameter difference | Config equal | Compute / Nextflow equal |
|---|---:|---|---|---|
| bwa | 41 | outdir | True | True / True |
| chromap | 41 | outdir | True | True / True |

Common checked settings: read_length=50; macs_gsize=2701262066; keep_dups=False; mito_name=chrM; skip_multiqc=False.

This independent comparison checks reviewed prepared payloads and their exact hashes. API-observed commits and collection identities are verified separately. Supplied config concerns Chromap recovery transport and is equal within each pair. No private payload contents are embedded.

## Measured outputs

Δ is fixed minus unfixed using exact decimal arithmetic. Flagstat values sum QC-passed and QC-failed **read records**, including properly paired records. JSON preserves both components. Merged-replicate inputs are derived sums. No tolerance-based acceptance is applied.

### BWA

Per-library cleaned outputs:

| Library / group | Metric | Unfixed | Fixed | Δ |
|---|---|---:|---:|---:|
| HIV_CD86HI_48H_REP1 | Raw input pairs | 21,260,206 | 21,260,206 | 0 |
| HIV_CD86HI_48H_REP1 | Cleaned total reads | 5,215,726 | 5,214,522 | -1204 |
| HIV_CD86HI_48H_REP1 | Cleaned mapped reads | 5,215,726 | 5,214,522 | -1204 |
| HIV_CD86HI_48H_REP1 | Cleaned properly paired reads | 5,140,616 | 5,138,634 | -1982 |
| HIV_CD86HI_48H_REP1 | Cleaned duplicate-flagged reads | 0 | 0 | 0 |
| HIV_CD86HI_48H_REP1 | BigWig scale factor | 0.191728 | 0.191772 | +0.000044 |
| HIV_CD86HI_48H_REP1 | MACS3 peak count | 30436.0 | 30438.0 | +2.0 |
| HIV_CD86HI_48H_REP1 | FRiP | 0.216445 | 0.216448 | +0.000003 |
| HIV_CD86HI_48H_REP2 | Raw input pairs | 20,649,365 | 20,649,365 | 0 |
| HIV_CD86HI_48H_REP2 | Cleaned total reads | 7,443,774 | 7,442,266 | -1508 |
| HIV_CD86HI_48H_REP2 | Cleaned mapped reads | 7,443,774 | 7,442,266 | -1508 |
| HIV_CD86HI_48H_REP2 | Cleaned properly paired reads | 7,359,036 | 7,357,266 | -1770 |
| HIV_CD86HI_48H_REP2 | Cleaned duplicate-flagged reads | 0 | 0 | 0 |
| HIV_CD86HI_48H_REP2 | BigWig scale factor | 0.13434 | 0.134368 | +0.000028 |
| HIV_CD86HI_48H_REP2 | MACS3 peak count | 35860.0 | 35854.0 | -6.0 |
| HIV_CD86HI_48H_REP2 | FRiP | 0.230036 | 0.23001 | -0.000026 |
| MOCK_48H_REP1 | Raw input pairs | 21,344,854 | 21,344,854 | 0 |
| MOCK_48H_REP1 | Cleaned total reads | 5,676,724 | 5,676,056 | -668 |
| MOCK_48H_REP1 | Cleaned mapped reads | 5,676,724 | 5,676,056 | -668 |
| MOCK_48H_REP1 | Cleaned properly paired reads | 5,629,646 | 5,628,814 | -832 |
| MOCK_48H_REP1 | Cleaned duplicate-flagged reads | 0 | 0 | 0 |
| MOCK_48H_REP1 | BigWig scale factor | 0.176158 | 0.176179 | +0.000021 |
| MOCK_48H_REP1 | MACS3 peak count | 36521.0 | 36551.0 | +30.0 |
| MOCK_48H_REP1 | FRiP | 0.198293 | 0.198316 | +0.000023 |
| MOCK_48H_REP2 | Raw input pairs | 23,834,826 | 23,834,826 | 0 |
| MOCK_48H_REP2 | Cleaned total reads | 8,364,076 | 8,362,892 | -1184 |
| MOCK_48H_REP2 | Cleaned mapped reads | 8,364,076 | 8,362,892 | -1184 |
| MOCK_48H_REP2 | Cleaned properly paired reads | 8,272,454 | 8,270,044 | -2410 |
| MOCK_48H_REP2 | Cleaned duplicate-flagged reads | 0 | 0 | 0 |
| MOCK_48H_REP2 | BigWig scale factor | 0.119559 | 0.119576 | +0.000017 |
| MOCK_48H_REP2 | MACS3 peak count | 51624.0 | 51633.0 | +9.0 |
| MOCK_48H_REP2 | FRiP | 0.251002 | 0.250963 | -0.000039 |

Merged-replicate outputs:

| Library / group | Metric | Unfixed | Fixed | Δ |
|---|---|---:|---:|---:|
| HIV_CD86HI_48H | Derived input pairs | 41,909,571 | 41,909,571 | 0 |
| HIV_CD86HI_48H | Cleaned total reads | 12,659,500 | 12,656,788 | -2712 |
| HIV_CD86HI_48H | Cleaned mapped reads | 12,659,500 | 12,656,788 | -2712 |
| HIV_CD86HI_48H | Cleaned properly paired reads | 12,499,652 | 12,495,900 | -3752 |
| HIV_CD86HI_48H | Cleaned duplicate-flagged reads | 0 | 0 | 0 |
| HIV_CD86HI_48H | BigWig scale factor | 0.0789921 | 0.079009 | +0.0000169 |
| HIV_CD86HI_48H | MACS3 peak count | 70213.0 | 69791.0 | -422.0 |
| HIV_CD86HI_48H | FRiP | 0.275028 | 0.274689 | -0.000339 |
| MOCK_48H | Derived input pairs | 45,179,680 | 45,179,680 | 0 |
| MOCK_48H | Cleaned total reads | 14,040,800 | 14,038,948 | -1852 |
| MOCK_48H | Cleaned mapped reads | 14,040,800 | 14,038,948 | -1852 |
| MOCK_48H | Cleaned properly paired reads | 13,902,100 | 13,898,858 | -3242 |
| MOCK_48H | Cleaned duplicate-flagged reads | 0 | 0 | 0 |
| MOCK_48H | BigWig scale factor | 0.071221 | 0.0712304 | +0.0000094 |
| MOCK_48H | MACS3 peak count | 88651.0 | 88666.0 | +15.0 |
| MOCK_48H | FRiP | 0.281133 | 0.281163 | +0.000030 |

Library-derived consensus:

- BED: 74,935 → 74,895 intervals; 69,596 exact shared; only unfixed/fixed 5,339/5,299; exact interval Jaccard **0.8674128175087868**; covered-base Jaccard **0.9928887420273258**.
- Counts: **6,982 changed cells**, 69,596 shared coordinates; featureCounts v2.0.1 → v2.0.1; columns: HIV_CD86HI_48H_REP1, HIV_CD86HI_48H_REP2, MOCK_48H_REP1, MOCK_48H_REP2.

| Library | Total unfixed | Total fixed | Δ total | Changed shared intervals | Sum absolute Δ | Max absolute Δ |
|---|---:|---:|---:|---:|---:|---:|
| HIV_CD86HI_48H_REP1 | 755,866 | 755,472 | -394 | 1,410 | 1,564 | 7 |
| HIV_CD86HI_48H_REP2 | 1,049,954 | 1,049,186 | -768 | 2,243 | 2,602 | 7 |
| MOCK_48H_REP1 | 728,600 | 728,326 | -274 | 1,079 | 1,152 | 7 |
| MOCK_48H_REP2 | 1,207,725 | 1,207,245 | -480 | 2,250 | 2,552 | 8 |

Merged-replicate-derived consensus:

- BED: 116,221 → 115,880 intervals; 108,451 exact shared; only unfixed/fixed 7,770/7,429; exact interval Jaccard **0.8770804690659119**; covered-base Jaccard **0.9913517830497219**.
- Counts: **7,143 changed cells**, 108,451 shared coordinates; featureCounts v2.0.1 → v2.0.1; columns: HIV_CD86HI_48H_REP1, HIV_CD86HI_48H_REP2, MOCK_48H_REP1, MOCK_48H_REP2.

| Library | Total unfixed | Total fixed | Δ total | Changed shared intervals | Sum absolute Δ | Max absolute Δ |
|---|---:|---:|---:|---:|---:|---:|
| HIV_CD86HI_48H_REP1 | 849,066 | 848,202 | -864 | 1,450 | 1,590 | 6 |
| HIV_CD86HI_48H_REP2 | 1,153,180 | 1,152,042 | -1,138 | 2,305 | 2,666 | 7 |
| MOCK_48H_REP1 | 835,699 | 835,329 | -370 | 1,066 | 1,121 | 4 |
| MOCK_48H_REP2 | 1,335,504 | 1,334,980 | -524 | 2,322 | 2,612 | 8 |

### CHROMAP

Per-library cleaned outputs:

| Library / group | Metric | Unfixed | Fixed | Δ |
|---|---|---:|---:|---:|
| HIV_CD86HI_48H_REP1 | Raw input pairs | 21,260,206 | 21,260,206 | 0 |
| HIV_CD86HI_48H_REP1 | Cleaned total reads | 5,101,672 | 5,102,390 | +718 |
| HIV_CD86HI_48H_REP1 | Cleaned mapped reads | 5,101,672 | 5,102,390 | +718 |
| HIV_CD86HI_48H_REP1 | Cleaned properly paired reads | 5,101,672 | 5,102,390 | +718 |
| HIV_CD86HI_48H_REP1 | Cleaned duplicate-flagged reads | 0 | 0 | 0 |
| HIV_CD86HI_48H_REP1 | BigWig scale factor | 0.196014 | 0.195987 | -0.000027 |
| HIV_CD86HI_48H_REP1 | MACS3 peak count | 30478.0 | 30501.0 | +23.0 |
| HIV_CD86HI_48H_REP1 | FRiP | 0.227356 | 0.22754 | +0.000184 |
| HIV_CD86HI_48H_REP2 | Raw input pairs | 20,649,365 | 20,649,365 | 0 |
| HIV_CD86HI_48H_REP2 | Cleaned total reads | 7,267,790 | 7,269,776 | +1986 |
| HIV_CD86HI_48H_REP2 | Cleaned mapped reads | 7,267,790 | 7,269,776 | +1986 |
| HIV_CD86HI_48H_REP2 | Cleaned properly paired reads | 7,267,790 | 7,269,776 | +1986 |
| HIV_CD86HI_48H_REP2 | Cleaned duplicate-flagged reads | 0 | 0 | 0 |
| HIV_CD86HI_48H_REP2 | BigWig scale factor | 0.137593 | 0.137556 | -0.000037 |
| HIV_CD86HI_48H_REP2 | MACS3 peak count | 35646.0 | 35640.0 | -6.0 |
| HIV_CD86HI_48H_REP2 | FRiP | 0.239107 | 0.239254 | +0.000147 |
| MOCK_48H_REP1 | Raw input pairs | 21,344,854 | 21,344,854 | 0 |
| MOCK_48H_REP1 | Cleaned total reads | 5,553,678 | 5,554,034 | +356 |
| MOCK_48H_REP1 | Cleaned mapped reads | 5,553,678 | 5,554,034 | +356 |
| MOCK_48H_REP1 | Cleaned properly paired reads | 5,553,678 | 5,554,034 | +356 |
| MOCK_48H_REP1 | Cleaned duplicate-flagged reads | 0 | 0 | 0 |
| MOCK_48H_REP1 | BigWig scale factor | 0.180061 | 0.180049 | -0.000012 |
| MOCK_48H_REP1 | MACS3 peak count | 36449.0 | 36318.0 | -131.0 |
| MOCK_48H_REP1 | FRiP | 0.205499 | 0.205352 | -0.000147 |
| MOCK_48H_REP2 | Raw input pairs | 23,834,826 | 23,834,826 | 0 |
| MOCK_48H_REP2 | Cleaned total reads | 8,178,346 | 8,180,562 | +2216 |
| MOCK_48H_REP2 | Cleaned mapped reads | 8,178,346 | 8,180,562 | +2216 |
| MOCK_48H_REP2 | Cleaned properly paired reads | 8,178,346 | 8,180,562 | +2216 |
| MOCK_48H_REP2 | Cleaned duplicate-flagged reads | 0 | 0 | 0 |
| MOCK_48H_REP2 | BigWig scale factor | 0.122274 | 0.122241 | -0.000033 |
| MOCK_48H_REP2 | MACS3 peak count | 50704.0 | 50729.0 | +25.0 |
| MOCK_48H_REP2 | FRiP | 0.258664 | 0.258836 | +0.000172 |

Merged-replicate outputs:

| Library / group | Metric | Unfixed | Fixed | Δ |
|---|---|---:|---:|---:|
| HIV_CD86HI_48H | Derived input pairs | 41,909,571 | 41,909,571 | 0 |
| HIV_CD86HI_48H | Cleaned total reads | 12,369,462 | 12,372,166 | +2704 |
| HIV_CD86HI_48H | Cleaned mapped reads | 12,369,462 | 12,372,166 | +2704 |
| HIV_CD86HI_48H | Cleaned properly paired reads | 12,369,462 | 12,372,166 | +2704 |
| HIV_CD86HI_48H | Cleaned duplicate-flagged reads | 0 | 0 | 0 |
| HIV_CD86HI_48H | BigWig scale factor | 0.0808443 | 0.0808266 | -0.0000177 |
| HIV_CD86HI_48H | MACS3 peak count | 68273.0 | 67979.0 | -294.0 |
| HIV_CD86HI_48H | FRiP | 0.282848 | 0.282765 | -0.000083 |
| MOCK_48H | Derived input pairs | 45,179,680 | 45,179,680 | 0 |
| MOCK_48H | Cleaned total reads | 13,732,024 | 13,734,596 | +2572 |
| MOCK_48H | Cleaned mapped reads | 13,732,024 | 13,734,596 | +2572 |
| MOCK_48H | Cleaned properly paired reads | 13,732,024 | 13,734,596 | +2572 |
| MOCK_48H | Cleaned duplicate-flagged reads | 0 | 0 | 0 |
| MOCK_48H | BigWig scale factor | 0.0728225 | 0.0728088 | -0.0000137 |
| MOCK_48H | MACS3 peak count | 86275.0 | 86331.0 | +56.0 |
| MOCK_48H | FRiP | 0.287599 | 0.2877 | +0.000101 |

Library-derived consensus:

- BED: 73,670 → 73,568 intervals; 68,598 exact shared; only unfixed/fixed 5,072/4,970; exact interval Jaccard **0.8723041709053917**; covered-base Jaccard **0.9940572916380384**.
- Counts: **8,065 changed cells**, 68,598 shared coordinates; featureCounts v2.0.1 → v2.0.1; columns: HIV_CD86HI_48H_REP1, HIV_CD86HI_48H_REP2, MOCK_48H_REP1, MOCK_48H_REP2.

| Library | Total unfixed | Total fixed | Δ total | Changed shared intervals | Sum absolute Δ | Max absolute Δ |
|---|---:|---:|---:|---:|---:|---:|
| HIV_CD86HI_48H_REP1 | 760,127 | 760,435 | +308 | 1,675 | 1,855 | 5 |
| HIV_CD86HI_48H_REP2 | 1,054,408 | 1,055,027 | +619 | 2,633 | 3,060 | 7 |
| MOCK_48H_REP1 | 728,717 | 728,350 | -367 | 1,191 | 1,251 | 3 |
| MOCK_48H_REP2 | 1,208,273 | 1,208,796 | +523 | 2,566 | 2,912 | 8 |

Merged-replicate-derived consensus:

- BED: 112,658 → 112,481 intervals; 105,694 exact shared; only unfixed/fixed 6,964/6,787; exact interval Jaccard **0.8848758842982125**; covered-base Jaccard **0.9933891982677342**.
- Counts: **8,291 changed cells**, 105,694 shared coordinates; featureCounts v2.0.1 → v2.0.1; columns: HIV_CD86HI_48H_REP1, HIV_CD86HI_48H_REP2, MOCK_48H_REP1, MOCK_48H_REP2.

| Library | Total unfixed | Total fixed | Δ total | Changed shared intervals | Sum absolute Δ | Max absolute Δ |
|---|---:|---:|---:|---:|---:|---:|
| HIV_CD86HI_48H_REP1 | 848,108 | 848,068 | -40 | 1,709 | 1,886 | 5 |
| HIV_CD86HI_48H_REP2 | 1,152,115 | 1,152,354 | +239 | 2,702 | 3,109 | 7 |
| MOCK_48H_REP1 | 830,705 | 830,680 | -25 | 1,212 | 1,274 | 5 |
| MOCK_48H_REP2 | 1,330,099 | 1,330,645 | +546 | 2,668 | 3,022 | 8 |

## Interpretation, provenance and ambiguities

High covered-base Jaccard does not mean identical intervals: shifted boundaries can preserve almost all covered bases while changing many exact interval keys. BWA library consensus has exact Jaccard 86.74% versus covered-base Jaccard 99.29%. These are measured differences, not equivalence.

Count comparisons join coordinates and library names, ignoring unstable interval IDs and row/column order. Own-arm totals use each full interval set. Changed-cell statistics and any correlation use only exact shared coordinates; nonshared rows are excluded from those calculations and remain explicit in `comparison.json`.

Peak counts/FRiP come only from unambiguous collected MultiQC `report_saved_raw_data` entries. Consensus summaries come from guarded `comparison.json`, which preserves full coordinate/cell differences. Individual library broadPeak coordinates are not assumed collected; BED overlap concerns consensus files.

A separate review observed identical numeric BED/SAF starts in both source arms rather than explicit BED→SAF conversion. This is an unverified shared observation, not a newly confirmed bug, and is not attributed to PR448. No cross-format biological coordinate equivalence is asserted.

BAM byte/read-name equality, BigWig signal comparison, plot interpretation, biological differential inference and proof that the pipeline is bug-free are outside scope. Success and comparison completeness establish execution/coverage.

- No parser/source ambiguity was detected.

Accompanying JSON retains full source pins, input/artifact hashes, QC splits, parameter-evidence hash and generator identity. No credentials, private payload contents or private source storage paths are embedded.
