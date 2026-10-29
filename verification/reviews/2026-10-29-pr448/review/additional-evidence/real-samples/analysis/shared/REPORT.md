# Three-arm real BAM analysis

**COMPLETE_ANALYSIS** — analysis completeness is not a scientific PASS.

Retained counts below apply only duplicate flags to marked paired-primary BAM fragments, before blacklist, mitochondrial, mapping-quality and downstream orphan filtering.

## D28_REP1

Cross-RG families with unfixed excess: 2553; extra retained fragments: 2553.

| Pair | All coordinate counts equal | Retained coordinate counts equal | Retained QNAME membership equal |
|---|---|---|---|
| base_vs_fixed | True | True | True |
| base_vs_unfixed | True | False | False |
| fixed_vs_unfixed | True | False | False |
## D28P_REP1

Cross-RG families with unfixed excess: 1865; extra retained fragments: 1865.

| Pair | All coordinate counts equal | Retained coordinate counts equal | Retained QNAME membership equal |
|---|---|---|---|
| base_vs_fixed | True | True | True |
| base_vs_unfixed | True | False | False |
| fixed_vs_unfixed | True | False | False |

## Errors


## Limits

- Biological libraries stay separated by the harness OUTPUT identity; LB tags are audited, never used to merge conditions.
- Fragments use both primary mapped mates, grouped by (RG,QNAME), with canonical reference/unclipped-5-prime/orientation endpoints.
- Only reciprocal mate coordinates and one read1/read2 are paired. Orphans, ambiguous QNAME groups, unmapped, secondary and supplementary records are counted separately.
- Without RG, indistinguishable colliding QNAMEs cannot always be resolved; groups with more than one mate per slot are excluded, not cross-paired.
- Retained means duplicate-flag filtering of paired primary mapped records in marked BAMs, before blacklist, mitochondrial, mapping-quality or downstream orphan filtering; mixed-flag pairs are reported separately.
- Coordinate counts and retained QNAME membership are separate: Picard may choose different equivalent representatives. No read-name identity is assumed.
- Core digests summarize paired-eligible SAM fields 1-11 with the duplicate flag cleared; they are not BAM-byte hashes or a replacement for coordinate counts.
- Coordinate families do not reimplement Picard optical-distance, UMI or representative-scoring rules; their measured retained multiplicities are reported separately.
- Cross-RG families identify an unfixed excess, not proof that the source accessions are technical replicates; metadata validation remains external.
