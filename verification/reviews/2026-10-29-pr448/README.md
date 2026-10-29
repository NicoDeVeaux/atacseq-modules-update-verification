# PR448 full-data verification

All four HIV workflows succeeded on reviewed dev `73155d` and proposed fix `a9b588`, using BWA and Chromap. Each processed **87,089,251 read pairs**. The independent audit verified **324 artifacts**, source/workflow identities and all raw FastQC mate counts.

| Check | Result |
|---|---|
| Fixed BWA vs archived original dev | All 74,895 regions and 299,580 count cells match exactly |
| Unfixed BWA vs archived PR448 | Count matrix matches exactly |
| Dev → fix, BWA | −4,564 cleaned reads; consensus covered-base Jaccard 99.29% |
| Dev → fix, Chromap | +5,276 cleaned reads; consensus covered-base Jaccard 99.41% |
| Identical-alignment resequencing control | Pre-448/fixed duplicate marking agrees exactly; dev retains 2,553/1,865 extra duplicate pairs |
| Three resequencing core workflows | Peak coordinates and all 1,934 consensus regions match pre-448/fixed; one count cell differs by one and is traced |

The proposed mitigation updates Trim Galore to 2.3.0 with `--no_poly_g`, and separately shares Chromap library IDs across technical runs while keeping distinct read-group IDs. [Issue draft](PR448-ISSUE-DRAFT.md).

## Independent review

Start with the [review guide](review/REVIEW.md) and [claim/source/run map](review/CLAIMS.json). The [exact source snapshot](review/PIPELINE-SOURCE.json) records fork commit `1d840c`; tracked code and its proposed patch are included. Full-data runs test the earlier two-fix proposal `a9b588`. Later PRESEQ and GFFREAD corrections have separate targeted evidence.

The [original trimming/read-group controls](module-review/original-fixes/README.md) preserve the small triggering fixtures and task evidence. The [alignment/QC audit](module-review/alignment/README.md) and [version/wrapper scan](module-review/modules/README.md) preserve actual comparisons, pins and exclusions. The integrity verifier checks bytes and inventory, not scientific correctness. Run `python3 -B test_bundle_integrity.py` for corruption/inventory negative controls.

## Computation and files

- [Full HIV results](hiv/results/FINAL-REPORT.md), [independent audit](hiv/results/AUDIT.md), [historical agreement](hiv/results/HISTORICAL-AGREEMENT.md).
- [Portable HIV reproduction](portable/README.md): complete pinned sources/licenses, exact scientific settings, public inputs/checksums, isolated execution and comparison code. Seven behavior tests and four configuration parses passed.
- [Complete resequencing control](resequencing/README.md): ten ordered archive parts preserve all 4,565 files, including actual FASTQ subsets, common-alignment and cleaned BAMs, matched yeast reference/annotation, all 469 task evidence sets, reports and replay scripts. All members and a deterministic rebuild were verified; 18 existing tests pass.
- [Cloud execution archives](hiv/CLOUD-ARCHIVES.json): split archives of sanitized commands, stdout/stderr/exit codes, scientific text and provenance, with per-member original/public hashes.
- [All published cloud files](hiv/inventory/published-file-inventory.tsv): 2,686 objects totaling 43.84 GB. Full output-tree archiving is being prepared in an **unpublished draft release**; `RELEASE.json` records the plan. Completion requires verified part/member manifests and actual release assets.

Verify the distributed bytes and archive members without downloading or launching workflows:

```sh
python3 -B verify.py --deep
python3 -B portable/tools/verify_public.py --bundle portable --manifest BUNDLE-MANIFEST.json
python3 -B resequencing/verify_parts.py
```

The HIV cohort has one technical run per library, so the separate resequencing experiment supplies the direct Chromap library-ID control. That experiment uses two real libraries sequenced twice and 1,000,000 genuine pairs against sacCer3. Raw 101-base reads are unchanged; the supported 100-base bin selects effective genome size. Historical FASTQ byte identity is not established.

Private paths are normalized, with original and distributed hashes separated. Nested packages preserve their staging-time records; this index and `RELEASE.json` describe integration status. Reference-byte and resolved-container-digest gaps are documented in the portable manifest. The private Co-Scientist billing investigation is retained separately.

This is written by GPT-6 (Codex) on Nico DeVeaux’s behalf.
