# Public data migration

The supporting repository is the canonical public location for ATACseq validation evidence. The user authorized deleting local data once its public copy was verified. This supersedes the earlier local hold only for data actually preserved publicly; private and unmatched files remain outside that cleanup.

The [remote content index](remote-content-index.json.gz) records actual anonymous downloads, including every Git blob and published release asset, reconstructed archives and regular archive members. It pins the commit and exact SHA256/size identities with retrieval locations; manifest-only or draft-release hashes are excluded. Decompress it and check [the uncompressed SHA256](remote-content-index.sha256) before using it as a lookup catalog. Existing package READMEs describe ordered-part reconstruction.

Newly published evidence includes the [complete count and SAF witnesses](../2026-11-03-count-saf-data/README.md) and [fingerprint report data](../2026-11-03-fingerprint-reporting/data/README.md). Local deletion is performed file by file after a fresh identity, Git-boundary and SHA256 check; code, credentials, unknown files and unpublished bulk assets are retained. A final receipt will record actual removals separately from the candidate inventory.

This is written by an AI agent (model name unavailable) on Nico DeVeaux’s behalf.
