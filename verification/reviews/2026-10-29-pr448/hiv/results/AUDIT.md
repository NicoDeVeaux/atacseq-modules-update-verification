# Independent full-data HIV audit

State: INDEPENDENT_AUDIT_COMPLETE. No scientific PASS is implied.

All four reviewed workflow identities, source/payload pins and downloaded artifact checksums match. Each arm reports 87,089,251 raw read pairs.

| Aligner | Library | Unfixed retained pairs | Fixed retained pairs | Fixed − unfixed | Unfixed scale | Fixed scale |
|---|---|---:|---:|---:|---:|---:|
| bwa | HIV_CD86HI_48H_REP1 | 2607863 | 2607261 | -602 | 0.191728 | 0.191772 |
| bwa | HIV_CD86HI_48H_REP2 | 3721887 | 3721133 | -754 | 0.13434 | 0.134368 |
| bwa | MOCK_48H_REP1 | 2838362 | 2838028 | -334 | 0.176158 | 0.176179 |
| bwa | MOCK_48H_REP2 | 4182038 | 4181446 | -592 | 0.119559 | 0.119576 |
| chromap | HIV_CD86HI_48H_REP1 | 2550836 | 2551195 | 359 | 0.196014 | 0.195987 |
| chromap | HIV_CD86HI_48H_REP2 | 3633895 | 3634888 | 993 | 0.137593 | 0.137556 |
| chromap | MOCK_48H_REP1 | 2776839 | 2777017 | 178 | 0.180061 | 0.180049 |
| chromap | MOCK_48H_REP2 | 4089173 | 4090281 | 1108 | 0.122274 | 0.122241 |

Limits:

- This compares upstream dev73155d with proposeda9b588 for BWA and Chromap; it is not a pre-PR448 comparison.
- There is one technical run per biological library in this cohort. It cannot isolate cross-run read-group-library duplicate merging; the separate resequencing study supplies that control.
- Full input size is evidenced by all eight raw FastQC mate counts in each downloaded MultiQC JSON, cross-checked with its general statistics and recorded ENA cohort; this audit does not redownload or MD5-check the raw FASTQ bytes.
- Successful API status and physical workflow identity are drawn from saved accepted receipts, live observations and verified collection metadata; no fresh API or credential access is performed.
- Completion verifies identity, artifact integrity, full raw read counts and direct clN/scale measurements; it is not scientific PASS or proof of equivalence.
