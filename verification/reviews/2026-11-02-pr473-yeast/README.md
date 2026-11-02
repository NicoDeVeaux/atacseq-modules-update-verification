# #473 matched native yeast qualification

The independent actual-output checker passes for the matched native yeast GTF/GFF3 campaign at [source 4def83](https://github.com/NicoDeVeaux/atacseq-nfcore/tree/4def83f6c0d095c7c3ad315b3167916e9710b173), Nextflow 26.04.6. Both scientific workflows succeeded. This is bounded software qualification, not biological or all-input equivalence.

Two genuine libraries, D28 (SRR19479022/23) and D28P (SRR19479020/21), were each sequenced twice. Each arm uses four 250,000-pair prefixes, matched Ensembl R64-1-1 references, Chromap and real PRESEQ execution. The [report](REPORT.md) records the successful arms, original rejected filename attempt, quantitative comparisons and annotation limits.

The native GFF conversion omits **91 transposable-element transcripts**. Complete annotation equality is not claimed. The 1,934 consensus intervals are measured on these new Ensembl captures, not inherited from the earlier UCSC oracle. Historical full-HIV workflows remain pinned to `a9b588` and are not relabeled here.

The archive accounts for all 677 captured result files: 336 GTF, 337 corrected GFF and four from the rejected startup attempt. Original scientific files are byte-exact; private-context reports/params/trace have separate declared public copies with original/public hashes and decoded-content proofs. Inputs, native references, pinned source/license, portable checks and normalized task evidence are included. Raw captures remain privately held until #473 is resolved.

Run `python3 -B verify_parts.py` to verify the complete public inventory, ordered parts and every archive member offline without extraction. The integrity verifier does not rerun scientific tools or independently establish scientific correctness. Per-file curation and supported-decoder limits remain explicit in the report.

This is written by an AI agent (model name unavailable) on Nico DeVeaux's behalf.
