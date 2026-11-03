# Public data and local cleanup

The [run/hash/results ledger](../../run-ledger/README.md) is the starting point for what ran and what was verified. It keeps full source/input/container identities when known, observed results, precise verification scopes, evidence links and explicit unknowns. Hash lookup and result search work offline.

The user clarified that the goal is this compact track record, with useful scientific witnesses; every intermediate does not need a public payload copy. Documented generated caches and redundant backup/spool files may be cleared after preserving that evidence. Earlier hold statements describe the prior policy. Source/Git, credentials, unique small results and private witnesses remain protected.

The [complete count/SAF witnesses](../2026-11-03-count-saf-data/README.md) and [fingerprint report data](../2026-11-03-fingerprint-reporting/data/README.md) remain public. The optional full HIV bulk archive remains incomplete/unpublished; completion is outside this compact-provenance cleanup.

[Removal receipts](CLEANUP-SUMMARY.json) distinguish exact-public duplicate removal from separately authorized crash-dump removal and subsequent provenance-based generated-cache removal. [Removed content identities](removed-public-content-identities.json.gz) map the first cleanup to exact public SHA256/size records. Later cache removal does not imply full payloads are downloadable.

The [generated-artifact hash inventory](generated-artifact-records.jsonl.gz) records 621 distinct identities across the next cache-removal batch. Its [binding](GENERATED-CACHE-BINDING.json) pins the published run ledger and retained-evidence inventory. These are derivation/identity records, with legacy unknowns explicit; no full payload upload is implied. Search a digest with `gzip -dc generated-artifact-records.jsonl.gz | rg HASH_PREFIX`.

Cleanup completed: 9,843 exact-public duplicates, 1,310 documented generated files and 31 separately approved crash dumps were removed. All 11,184 paths were checked absent. The phases observed about 51.35 GB more free space in total; APFS and concurrent filesystem activity can affect this measurement. All 2,422 required small evidence files remained present. [Generated-content removal identities](removed-generated-content-identities.json.gz) record the actual discarded hashes. Source/Git and credentials were retained.

The [anonymous remote content index](remote-content-index.json.gz) pins the actual downloaded Git/release/archive-member bytes. Check its [uncompressed SHA256](remote-content-index.sha256) before using it as a lookup catalog. Ordered-part reconstruction is documented beside each archive. Metadata-only or draft-release references do not count as public payload coverage.

This is written by an AI agent (model name unavailable) on Nico DeVeaux’s behalf.
