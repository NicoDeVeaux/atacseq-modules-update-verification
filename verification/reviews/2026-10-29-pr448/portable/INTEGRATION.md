# Integrate under `portable/`

Copy only the relative file paths listed by `BUNDLE-MANIFEST.json`, preserving
their paths under the target repository's `portable/` directory. Include the
manifest itself. Do not copy `sources/extracted/`, Python caches, validation run
directories, original private payloads, credentials or local session caches.
The extracted sources are a verified generated cache and can be recreated from
the two bundled source archives.

From the target repository root, verify distributed bytes without launching work:

```sh
python3 -B portable/tools/verify_public.py --bundle portable \
  --manifest BUNDLE-MANIFEST.json
python3 -B portable/tools/verify_public.py --bundle portable
```

All four historical HIV arms are now SUCCEEDED with complete 81-file collections:
324 original artifacts, and exactly 87,089,251 actual input pairs per arm. The
four observed software-version files are included. Sanitized final records are:

- `observed/final-summary.md`: measured outcome and detailed per-arm tables.
- `observed/final-report.json`: sanitized final report data, including actual
  per-mate raw FastQC counts and original used-artifact hash metadata.
- `observed/final-comparison.json`: complete scientific comparison results,
  preserving exact coordinate/cell/field differences while omitting private
  launch and observation envelopes.
- `observed/recorded-artifacts.json`: hashes and sizes of all 324 original
  collected artifacts. It is metadata, not a claim that all those payloads are
  distributed within `portable/`.

`observed/PUBLIC-MANIFEST.json` records the actual public bytes. For transformed
records, original and public SHA-256 values are deliberately separate. The
original recorded artifact hashes cannot verify separately sanitized copies;
such copies need their own public-byte mapping. Private Platform launch/storage
provenance is not claimed independently runnable from these public-only records.

The historical count computation remains runnable with the bundled matrices and
strict source-pinned comparator, as documented in `README.md`. It is independent
of metadata sanitization because coordinates/sample counts were not changed.
Fresh reproduction executions use `reproduce.py` and their own receipts; the
historical workflow IDs/statuses are never substituted for new observations.

No pipeline source, normalized scientific parameter, launcher configuration or
existing finalizer stage changed in this metadata refresh. Prior validation
remains seven passing behavior tests, four Nextflow configuration parses and the
static source/input/patch checks. Only public-byte checks and sanitization scans
were repeated. No scientific reruns, cloud launches or publication occurred.

If integration edits any distributed file, regenerate its public/hash mapping
as appropriate and reseal `BUNDLE-MANIFEST.json`; do not preserve stale hashes.
The final publication/repository layout is owned by the parent integration task.
