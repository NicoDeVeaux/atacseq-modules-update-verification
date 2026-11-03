# SAF correction separated from the module repair

The [complete public count/SAF data package](../2026-11-03-count-saf-data/README.md) now includes the actual tables, both cell-delta witnesses, annotation files and boundary fixture, with original/distributed hashes and an offline verifier.

[PR #474](https://github.com/nf-core/atacseq/pull/474) at [f28734](https://github.com/NicoDeVeaux/atacseq-nfcore/commit/f2873418faf719756d89022a6e9d2e4315c56a89) contains the module repairs and blocking PRESEQ retry test. Its production source is byte-identical to the pre-SAF qualified source. A fresh count-only replay using its actual converter and the four hash-verified preserved BWA BAMs matches **all 299,580 archived values**, all feature metadata and the historical assignment-summary bytes. BED and SAF output bytes match the legacy inputs exactly. No alignment or full workflow was rerun locally.

The inherited SAF defect is now [issue #475](https://github.com/nf-core/atacseq/issues/475) and [draft PR #476](https://github.com/nf-core/atacseq/pull/476), based directly on upstream dev. Its first commit adds the regression guard; its second adds Start+1. The standalone candidate is [20aef1](https://github.com/NicoDeVeaux/atacseq-nfcore/commit/20aef1aabd6efc066d3aff845fe45797a5bfdd53). The actual-source boundary fixture checks BED starts 0 and 100, unchanged BED bytes, corrected SAF starts 1 and 101, and a real featureCounts boundary count of 1 to 0. The exact semantic guard passes all 30 expected outcomes across 15 scenarios and both consensus levels.

The #474 split reverses only 102 known SAF-dependent MD5 positions across six files. Every other byte of those files remains unchanged. All seven resulting content arrays equal retained pre-SAF native observations. Of the original mixed candidate's 647 changed positions, 545 stay untouched; 79 restored positions still differ from the original golden because of the validated module repairs, leaving 624 changed positions overall. The skip-trimming snapshot is restored byte-for-byte to upstream; skip-consensus remains unaffected by the SAF split. No assertion, ignore rule or CI gate was relaxed.

Post-split native CI is running for [#474](https://github.com/nf-core/atacseq/actions/runs/41644797269) and [#476](https://github.com/nf-core/atacseq/actions/runs/41644325268). This report does not claim either new head has passed full CI. Standalone SAF snapshots require evidence from its own base; the combined candidate's expectations were not copied into #476.

The [earlier full count-impact experiment](../2026-11-03-pr474-count-acceptance/README.md) remains historical evidence for the combined candidate. Its 2,280 changed cells belong to the SAF intervention; the corrected coordinates do not claim equality with legacy counts.

Limits: both local recounts use a pinned official Subread 2.0.1 image with an exact legacy positive control; the historical cloud image digest is unavailable. Earlier resequencing/duplicate-marking evidence remains separate. All validation data is retained locally and privately backed up; none was deleted.

This is written by an AI agent (model name unavailable) on Nico DeVeaux’s behalf.
