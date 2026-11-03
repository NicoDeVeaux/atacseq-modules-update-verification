# PR476: SAF snapshot update

[PR #476](https://github.com/nf-core/atacseq/pull/476) at [383f3a](https://github.com/NicoDeVeaux/atacseq-nfcore/commit/383f3ad30678ddba3e445d8aaaffaae36206e2ba) updates **104 MD5 fingerprints across six snapshot files** for the new SAF coordinates. Both Nextflow 25.10.4 and 26.10.5 emitted identical complete observed arrays in [the original CI run](https://github.com/nf-core/atacseq/actions/runs/41644325268).

| Output family | Updated fingerprints |
| --- | ---: |
| SAF annotations | 12 |
| featureCounts tables and assignment summaries | 24 |
| DESeq size factors | 44 |
| MultiQC featureCounts exports | 24 |

All other snapshot bytes are preserved: task counts, file names, directories, metadata, stub expectations and version fields. Both coordinate assertions, all other assertions, ignore rules and CI gates remain unchanged. The skip-consensus snapshot is unchanged. Independent integrity review replayed all twelve original failing logs and rejected 24 parser mutation controls. These checks establish precise edit/transport integrity; scientific correctness is not inferred from hashes alone.

The correction already has an actual-source boundary read reproduction and a [complete four-BAM intervention](../2026-11-03-pr474-count-acceptance/README.md). That large-cohort intervention uses the separately repaired BAMs and remains distinct from this standalone branch's CI inputs.

Two controls-report fingerprints are deliberately unchanged: `deeptools_plot_fingerprint_counts_mlib_deeptools.txt` and `mqc_deeptools_fingerprint_plot_1.txt`. These are deepTools fingerprint exports, with no direct SAF dependency, rather than featureCounts-derived reports. The first audit grouped any `mqc_` file as a count report; that classification was corrected before commit, reducing the SAF selection from 105 to 104.

Ten bounded replays of the actual MultiQC 1.13 implementation establish that a duplicate sample label can replace a previously captured curve according to unsorted file order. Unique-label controls are order invariant. Another serialization defect leaves float-keyed numeric cells blank in the counts TSV; equal-length duplicate curves can change plotted points without changing that TSV hash. The exact original/current CI hash pairs were not reproduced because genuine CI raw fingerprint inputs were not retained. Neither report fingerprint was accepted on this evidence. The raw fingerprint and QC-metrics files are already excluded by upstream's existing ignore policy; this PR does not expand those exclusions.

[Fresh CI recheck](https://github.com/nf-core/atacseq/actions/runs/41656579437) confirms all 104 updated SAF expectations match: **11/12 tests pass on each engine**. The sole failed test per engine is controls, differing only in the two retained deepTools report expectations. Overall CI remains red; neither report hash was waived or rebaselined. The previous green latest-version jobs contained raw test failures under the existing nonblocking policy; only original test summaries establish their result.

This is written by an AI agent (model name unavailable) on Nico DeVeaux’s behalf.

## Subsequent report-baseline refresh

Following review, [9a255c](https://github.com/NicoDeVeaux/atacseq-nfcore/commit/9a255c667bed26eec6759c94a1f8a01e281f623d) refreshes the two controls-report expectations to the pair reproduced in both CI runs on both engines. This pair also existed in the repository before [dfe474](https://github.com/nf-core/atacseq/commit/dfe47404770e320441421ae0e78f92469510465a), which changed exactly these two hashes in the opposite direction. This is a baseline update, not a reporting repair or a claim that the exact CI cause was reproduced. The proven MultiQC defects and their limits above remain open.

All six previously failing cases now have expected content exactly equal to both engines’ original complete observed arrays. Code, coordinate assertions, all other assertions and CI gates remain unchanged. [New native recheck](https://github.com/nf-core/atacseq/actions/runs/41666190365) is running.
