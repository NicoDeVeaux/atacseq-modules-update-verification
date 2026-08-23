# ATAC-seq consensus peak overlap

All peak sets are on **GRCh38** (UCSC `chr` naming). Overlap universe is built by merging every set's intervals into disjoint **union regions**; a set is a member of a region if it has >= 1 bp overlap. Membership-combination counts below partition the universe exactly.

## Set sizes

| Set | Raw peaks | Union regions covered |
|-----|----------:|----------------------:|
| paper_original | 87,681 | 84,183 |
| dev | 74,895 | 74,449 |
| branch | 74,935 | 74,486 |

## Intersection breakdown (UpSet)

| Combination | Union regions |
|-------------|--------------:|
| paper_original & dev & branch | 57,129 |
| paper_original | 26,927 |
| dev & branch | 17,153 |
| branch | 150 |
| dev | 94 |
| paper_original & dev | 73 |
| paper_original & branch | 54 |

## Pairwise Jaccard (union-region space)

| | paper_original | dev | branch |
|---|---|---|---|
| paper_original | 1.000 | 0.564 | 0.563 |
| dev | 0.564 | 1.000 | 0.995 |
| branch | 0.563 | 0.995 | 1.000 |

## Raw reciprocal overlap (asymmetric: % of row's peaks overlapping column)

| row \ col | paper_original | dev | branch |
|---|---|---|---|
| paper_original | - | 68.9% (60,405/87,681) | 68.9% (60,384/87,681) |
| dev | 77.0% (57,642/74,895) | - | 99.8% (74,724/74,895) |
| branch | 76.9% (57,626/74,935) | 99.7% (74,725/74,935) | - |

