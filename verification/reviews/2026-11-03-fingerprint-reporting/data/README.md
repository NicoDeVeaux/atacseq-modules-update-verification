# Public fingerprint reporting data

This compact package contains genuine fingerprint matrices, quality tables, scientific commands and exact numeric exports derived from public nf-core yeast datasets. `PUBLIC-INPUTS.json` pins all fourteen controls input objects and their scientific roles; each was downloaded anonymously and matched by SHA256 and Git blob hash. `PUBLIC-PROVENANCE.json` independently checks the controls and default sources, including their public yeast accessions.

Only public sample labels and accession filenames remain in the data. Complete MultiQC JSON/HTML, environment files, credentials, local paths, user or host identities, runtime configuration, work caches and BAM files are excluded. Numeric vectors were selected explicitly from the original report JSON. Copied raw matrices, quality tables and TXT exports retain their original bytes; their SHA256 hashes are recorded in `MANIFEST.json`. Command files contain presentation extracts of scientific argv and public version-reporting code; the environment-capture wrapper is omitted and original command hashes retained.

Verify with Python 3.9 or newer:

```bash
python3 verify.py
```

The verifier checks every declared file, all eight controls series/782 numeric points across five export scopes, the default six series/473 points, and all four legacy input orders. It checks sample identities, X/Y values, sparse blanks, unique columns and byte-identical controls exports. The legacy tables deliberately retain their empty numeric cells as evidence of the defect.

`sources/` includes the exact version-bound MultiQC 1.13 helper and effective public assets config. For parser/CLI execution, use the pinned image and commands in the proposal's [regression runbook](https://github.com/NicoDeVeaux/atacseq-nfcore/blob/826e7e8409b5891fee0f0f3bf0854a6df26e81ca/tests/regressions/fingerprint_reports.md). The source fixtures in that runbook are separately identified; this package contains the actual scientific reporting evidence.

Controls include the final-helper NF25 workflow, its reversed-input replay, the earlier-helper NF26 workflow and final-helper forward/reverse NF26 reporter replays. This does not claim a literal full NF26 workflow on the final helper, a native CI pass or nf-test assertion reruns. Default is a source-matched report replay; skip-consensus is derived rather than independently run. The legacy reproduction changes only headers on genuine retained vectors and does not recover historical CI files or their actual ordering. Four other profiles remain unqualified. The parent review records those limits and snapshot admission.

All local originals are retained until issue #473 resolves.

This is written by an AI agent (model name unavailable) on Nico DeVeaux’s behalf.
