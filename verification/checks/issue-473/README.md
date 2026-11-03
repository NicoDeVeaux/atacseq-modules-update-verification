# Manual checks for ATACseq issue 473

These opt-in checks run against a separate pipeline checkout. Pass its path with `--repo`; neither check runs in pipeline CI.

```bash
ATACSEQ_REPO=/path/to/atacseq
python3 verification/checks/issue-473/gffread_conversion.py --repo "$ATACSEQ_REPO"
uv run --with nf-core==4.0.3 python verification/checks/issue-473/module_patch_roundtrip.py --repo "$ATACSEQ_REPO"
```

GFFREAD conversion requires Docker, Python 3 and a cached Nextflow distribution. Run `nextflow -version` first, or select a cached distribution with `--nextflow-jar /path/to/nextflow-one.jar`. On the local Mac, add `--docker-context colima`. This checks the actual module's packaged runtime, two exon coordinates and gene/transcript identifiers on a benign annotation. It does not reproduce the original crash or prove all-input equivalence.

Patch roundtrip checks the exact upstream pins in `modules.json`, registered GFFREAD/PRESEQ patches, canonical regeneration and forward/reverse replay byte for byte. It uses nf-core/tools APIs, tested with 4.0.3 and 4.1.0; Trim Galore is an unpatched control. `--cache /path/to/cache` reuses upstream downloads.

Both scripts support `--output /path/to/empty-directory` to retain evidence. Original pipeline copies are preserved in [source 4b26f7](https://github.com/NicoDeVeaux/atacseq-nfcore/tree/4b26f7e58fc374b13184548a2d375e49f34dc5fa/tests/regressions); [MIGRATION.json](MIGRATION.json) records their hashes and the explicit-checkout adaptation.

The [PRESEQ retry check](https://github.com/NicoDeVeaux/atacseq-nfcore/blob/fix/pr448-module-regressions/tests/regressions/preseq_retry.py) stays in the pipeline repository as a blocking CI test. The [CI qualification report](../../reviews/2026-11-03-pr474-ci/README.md) records the earlier pipeline validation and its limits.
