# Captured task-source/result identities

This capsule records 4,464 preserved generated Nextflow task directories, with 1,901 distinct `.command.sh` SHA-256 values, 4,456 observed integer `.exitcode` files and 284 captured versions-file identities. Eight task directories have no observed exit file. Source script bodies and versions contents are not copied into the capsule.

The records identify current captured script bytes, an observed task result and their filesystem timestamp relationship. They do not independently establish that the script was unchanged since historical execution. Filesystem timestamps may reflect copying or archiving. Source-execution binding, pipeline Git and resolved container digest are explicitly unknown in this task-local capsule; separately guarded campaign evidence in the run ledger may establish some of those bindings.

An observed exit of zero is not scientific verification or a workflow PASS. Nonzero values can include deliberately failing controls. No browser, scientific tool or task script was executed for this inventory.

Personal root paths are replaced with opaque root IDs. The separate cleanup-association path map is retained privately and is not part of this public capsule. Only `.command.sh` bytes were read for hashing, small `.exitcode` values for parsing, and optional `versions.yml`/`versions.yaml` bytes for hashing. `.command.run`, `.command.env`, credentials, private staging, symlink targets and installed cache/library trees were excluded.

`TASK-SOURCE-CAPSULE.json.gz` expands to exactly `TASK-SOURCE-CAPSULE.json`. Verify the distributed identities with:

```sh
shasum -a 256 -c CHECKSUMS.txt
gzip -dc TASK-SOURCE-CAPSULE.json.gz | shasum -a 256
```

The streamed uncompressed digest should match `TASK-SOURCE-CAPSULE.sha256`. Captures include copied caches and synthetic controls; their count is not a count of distinct scientific executions.

This is written by an AI agent (model name unavailable) on Nico DeVeaux's behalf.
