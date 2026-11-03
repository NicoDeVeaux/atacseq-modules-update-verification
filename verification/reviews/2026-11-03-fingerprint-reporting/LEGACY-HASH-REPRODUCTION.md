# Original-label report hash reproduction

Both requested CI count/plot MD5 pairs reproduce exactly using the four genuine retained controls25 raw matrices, changing only their header line to the original `73155d` labels. The comment and every numeric-body byte are unchanged; original native producer files were reverified after replay.

| Effective last writer for shared REP1 control | Effective last writer for shared REP2 control | Counts MD5 | Numeric plot MD5 | Requested pair |
|---|---|---|---|---|
| SPT5_T0_REP1 | SPT5_T0_REP2 | `a9e79e` | `56a27c` | — |
| SPT5_T0_REP1 | SPT5_T15_REP2 | `eb7174` | `5dc805` | 1 |
| SPT5_T15_REP1 | SPT5_T0_REP2 | `16b75e` | `80da37` | 2 |
| SPT5_T15_REP1 | SPT5_T15_REP2 | `ec96c6` | `2fc603` | — |

Four effective orders cover the independent T0/T15 last-writer choice for each shared control. Four treatment curves remain distinct; two same-named control curves overwrite their earlier counterparts, leaving six series. The matching plot exports contain 588 and 585 actual numeric curve points, respectively. The legacy counts TSVs retain the MultiQC 1.13 serializer defect: six sample rows and zero numeric cells; this replay neither normalizes nor conceals that behavior.

The fast path uses the actual unmodified pinned MultiQC 1.13 raw parser, Base data writer, and linegraph numeric TXT writer with the exact retained pipeline assets config and TSV mode. The only substituted graphics call raises after the actual numeric TXT write. Before any counterfactual, that path reproduced the retained genuine eight-series/782-point plot TXT byte for byte (`7bb5e7`). The proposed helper is not imported. This is a library replay rather than a full CLI/report render. All five calibrated/order subprocesses exited zero in one cached-image container with shared dedicated HOME/font cache, network disabled, one CPU/two GiB.

This is **counterfactual reproduction using real retained vectors**, not recovered historical CI raw files or proof of their actual file ordering. It establishes that the two report pairs can arise solely from original labels and last-writer selection on these vectors. It does not independently establish every historical producer/input identity.

`local-evidence/old-hash-reproduction/INPUT-BINDINGS.json` binds native/captured originals, producer argv, numeric-body hashes and header-only copies. [LEGACY-HASH-REPRODUCTION.json](LEGACY-HASH-REPRODUCTION.json) records all four pairs and calibration. Every order retains exact TXT outputs and parser numeric mappings. Two initial setup-only harness failures are retained (missing report initialization, followed by an incorrect initializer name); the successful harness calls the real package `report.init()`. No application, snapshots, scientific inputs or original results changed; no BAM workflow or cloud execution ran.


This is written by an AI agent (model name unavailable) on Nico DeVeaux’s behalf.
