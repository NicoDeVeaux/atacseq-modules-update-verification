# Full count and SAF witnesses

[Download the complete data archive](count-saf-public.tar.gz?raw=true) (14.8 MB), verify its [SHA256](count-saf-public.tar.gz.sha256), then extract `count-saf-public/` and run its verifier. The [manifest](MANIFEST.json) lists all distributed files.

These selected public-study derivatives preserve the full four-library BWA count replay, its SAF intervention, the post-split legacy replay and the small actual featureCounts boundary fixture. The full cohort uses HIV_CD86HI_48H_REP1/REP2 and MOCK_48H_REP1/REP2, derived from public accessions SRR8508547, SRR8508548, SRR8508553 and SRR8508554. The tiny SAM is a separate constructed fixture.

`files/full-count/` includes the original BED/boolean/SAF, historical count tables, both local count outputs and assignment summaries, and both complete cell-delta witnesses. `files/post-split/` contains the restored #474 legacy outputs. `files/boundary/` includes the original/corrected BED, boolean input, SAF, SAM, counts and assignment summaries. Safe summaries and exact input identities already published by the supporting repository are copied under `files/provenance/`.

The legacy positive control matches all 299,580 archived count values. Start+1 changes 2,280 cells across 2,223 regions, decreasing the total by 2,293. The post-split #474 replay restores all 299,580 values. The boundary fixture changes one assigned count from 1 to 0. This isolates counting/coordinate behavior; it does not rerun alignment, peak calling or a complete workflow, and it does not prove every new count independently correct.

All scientific data rows, table headers, annotation coordinates, sample labels and numerical bytes are preserved. Five featureCounts comment lines contained an absolute executable spelling; only that spelling was reduced to the basename `featureCounts`. Per-file original/distributed hashes, transformations and identical noncomment-byte hashes are recorded in `MANIFEST.json`. BAMs, environment wrappers, credentials, raw launch records and local absolute paths are excluded.

The runtime was official Subread2.0.1 at the immutable image digest in the manifest. The historical cloud image digest is unavailable, so the complete legacy positive control supplies the local-image stage bridge. Full replay requires the four separately preserved BAMs identified in `files/provenance/INPUT-IDENTITIES.json`; they are not bundled here. Exact source commits and the scope of each observation remain in the manifest and the parent count-acceptance/SAF-split reports.

Verify selected bytes without scientific tools:

```sh
python3 -B verify.py
```

This verifies inventory and integrity. Scientific conclusions remain scoped to the recorded experiments.

This is written by an AI agent (model name unavailable) on Nico DeVeaux's behalf.
