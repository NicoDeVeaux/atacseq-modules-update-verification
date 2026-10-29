# Scientific-output regressions after #448: Trim Galore trimming and Chromap library IDs

I revisited the module updates in #448 because the original verification did not establish that scientific outputs were unchanged. I found two regressions and have put a proposed mitigation in [commit a9b588](https://github.com/NicoDeVeaux/atacseq-nfcore/commit/a9b588235e4a1ceb3c8838acad430628c5737c86).

1. **Trim Galore:** the update from 0.6.10 to 2.1.0 introduced default poly-G trimming, including an upstream bug that clipped poly-C from the wrong end of R2. My mitigation updates the complete module to **2.3.0** and passes **`--no_poly_g`** to preserve the previous trimming default. Upgrading alone does not restore that default.
2. **Chromap:** technical runs from the same biological library received different `RGLB` values. Picard therefore treated them as separate libraries and could retain duplicates across those runs. My mitigation derives `RGLB` from the biological-library ID by removing the terminal `_T<number>` suffix, while preserving each technical run's distinct `RGID`. This is a separate correction from the Trim Galore update.

## Verification

- **Original human HIV cohort:** I completed four full-data workflows—BWA and Chromap, each on reviewed dev `73155d` and the proposed fix `a9b588`. Every arm processed all **87,089,251 read pairs** across four libraries. The fixed BWA library-consensus matrix exactly matches the archived original dev matrix: **74,895 regions and all 299,580 count cells**. The new unfixed BWA matrix independently matches the archived PR448 matrix. This compares retained historical matrices; it is not a fresh execution of the immediate pre-448 parent.
- **Libraries sequenced twice:** Co-Scientist helped identify two real yeast ATAC libraries whose GEO records explicitly document resequencing. I tested 250,000 genuine pairs from each of four runs against sacCer3. With identical alignments supplied to the duplicate-marking paths, pre-448 and fixed outputs agree exactly; unfixed dev retains **2,553 and 1,865 additional duplicate pairs** in the two libraries. In the three core workflow runs, individual peak coordinates and all **1,934 consensus regions** match pre-448/fixed. One of 3,868 count cells differs by one; I traced that residual to a mapper/duplicate-representative difference and am not claiming complete output identity.

The HIV cohort has only one technical run per library, so the resequencing experiment supplies the direct control for the Chromap library-ID problem. Historical FASTQ byte identity has not been established.

The proposed fix is on [fix/pr448-module-regressions](https://github.com/NicoDeVeaux/atacseq-nfcore/tree/fix/pr448-module-regressions). Existing reproductions are in the [verification repository](https://github.com/NicoDeVeaux/atacseq-modules-update-verification/tree/main/verification/reviews/2026-10-28-pr448); I am adding the full computation, commands, checksums and run-output archive there. The new full-data archive is currently a draft, not yet published.

This is written by GPT-6 (Codex) on Nico DeVeaux’s behalf.
