# featureCounts count-change report: `dev` (baseline) vs `branch`

## Consensus peak set (intervals)

| Metric | Value |
|--------|-------|
| featureCounts version (dev) | `v2.0.1` |
| featureCounts version (branch) | `v2.1.1` |
| Intervals in dev | 74,895 |
| Intervals in branch | 74,935 |
| Shared intervals (by coord) | 69,596 |
| Intervals only in dev | 5,299 |
| Intervals only in branch | 5,339 |

## Per-sample read counts (over shared intervals)

`total_delta` = branch total - dev total. `changed_intervals` counts shared intervals whose count differs. `pearson_r` is over shared intervals.

| Sample | dev total | branch total | total delta | changed intervals | sum abs delta | max abs delta | Pearson r |
|--------|-----------:|-----------:|--------:|------------------:|-----:|-------:|----------:|
| HIV_CD86HI_48H_REP1 | 755,472 | 1,445,223 | +689,751 | 56,643 | 605,206 | 287 | 0.999411 |
| MOCK_48H_REP2 | 1,207,245 | 2,327,082 | +1,119,837 | 63,212 | 990,759 | 585 | 0.999567 |
| HIV_CD86HI_48H_REP2 | 1,049,186 | 2,018,283 | +969,097 | 59,405 | 838,263 | 522 | 0.999593 |
| MOCK_48H_REP1 | 728,326 | 1,391,601 | +663,275 | 58,623 | 598,037 | 469 | 0.999291 |


---

# featureCounts count-change report: `dev` (baseline) vs `pr448`

## Consensus peak set (intervals)

| Metric | Value |
|--------|-------|
| featureCounts version (dev) | `v2.0.1` |
| featureCounts version (pr448) | `v2.0.1` |
| Intervals in dev | 74,895 |
| Intervals in pr448 | 74,935 |
| Shared intervals (by coord) | 69,596 |
| Intervals only in dev | 5,299 |
| Intervals only in pr448 | 5,339 |

## Per-sample read counts (over shared intervals)

`total_delta` = pr448 total - dev total. `changed_intervals` counts shared intervals whose count differs. `pearson_r` is over shared intervals.

| Sample | dev total | pr448 total | total delta | changed intervals | sum abs delta | max abs delta | Pearson r |
|--------|-----------:|-----------:|--------:|------------------:|-----:|-------:|----------:|
| HIV_CD86HI_48H_REP1 | 755,472 | 755,866 | +394 | 1,410 | 1,564 | 7 | 0.999951 |
| MOCK_48H_REP2 | 1,207,245 | 1,207,725 | +480 | 2,250 | 2,552 | 8 | 0.999956 |
| HIV_CD86HI_48H_REP2 | 1,049,186 | 1,049,954 | +768 | 2,243 | 2,602 | 7 | 0.999955 |
| MOCK_48H_REP1 | 728,326 | 728,600 | +274 | 1,079 | 1,152 | 7 | 0.999956 |

