# Matched native GTF/GFF3 yeast campaign

The actual-output checker reports **passed=true**, no differences, and equal observed container digests for common task processes. Its gates include source/configuration, actual argv/versions, BAM/read groups, reference/input bindings and scientific output comparisons. The normalized checker result and collection records are preserved separately from archive integrity checks.

| Attempt | Workflow | Source / Nextflow | Outcome |
|---|---|---|---|
| GTF | `gtf` | `4def83` / 26.04.6 | SUCCEEDED; 20:24:08–20:51:08 UTC, 2026-11-02; 336 files |
| Original GFF startup | `gff-startup-rejected` | `4def83` / 26.04.6 | FAILED before scientific tasks; four files; excluded from successful-arm count |
| Corrected GFF | `gff3` | `4def83` / 26.04.6 | SUCCEEDED; ended 20:56:38 UTC, 2026-11-02; 337 files |

The official `.gff3.gz` basename was rejected by the pipeline filename schema. A byte-identical `.gff.gz` alias passed that same schema. No source or annotation content changed, and validation was not disabled. The original failure and its sanitized console remain explicit evidence.

| Observed output | Matched result |
|---|---|
| D28 peaks | 1,635 in each arm; coordinates equal |
| D28P peaks | 1,431 in each arm; coordinates equal |
| Consensus | 1,934 intervals in each arm; coordinates equal |
| Consensus counts | All 3,868 sample/coordinate cells unchanged |
| Retained fragments | D28: 282,467; D28P: 283,754; exact agreement across arms |
| PRESEQ | Both libraries' 10,000-row curves byte-identical across arms |
| Task container identity | Observed immutable digests agree across common processes |

The new 1,934-region result is independently measured from these native Ensembl captures. The earlier UCSC 1,934-region result is a different oracle and was not assumed. Collection binds all 185 task digests and 13 critical command attempts, all at attempt 1. No natural retry is claimed. Successful matching PRESEQ curves do not by themselves establish scientific validity; the separate stand-in mutation check remains the retry-causality control.

## Native annotation limit

Default fixed GFFREAD conversion contains 7,036 of 7,127 native GFF3 transcripts: **91 `transposable_element` transcripts are absent**, with no extra transcripts in the conversion preflight. The missing-ID inventory is preserved. The checker respects this declared feature scope and the native CDS/stop-codon convention comparison; it does not establish complete annotation equality or conceal these omissions.

## Curation and retention

All 677 captured files were audited without changing their originals. The result inventory contains 583 exact scientific files, 76 other exact files and 18 separate sanitized presentation copies. No private-metadata blocker was identified in supported binary scientific audits.

Audits decode complete BGZF BAMs/headers, every FastQC ZIP member, HTML LZString/gzip/base64/JSON payloads, image pixels/text metadata, PDF objects/decoded streams/page text/images and parsed SVG/XML. Complete literal scans cover unchanged bigWig/index/BAI files; unsupported hidden metadata decoding is not claimed. Artifact JavaScript and captured scientific commands were not executed by curation.

Each successful public MultiQC copy replaces two opaque legacy MTX/EOT font fallbacks with generated empty fonts. The opaque originals were not decoded or redistributed in those presentation copies; legacy EOT glyph rendering is not certified. Modern alternatives and scientific plot JSON non-string/numerical tokens are unchanged. Original reports remain privately retained.

Private storage/work paths, service links, ephemeral capabilities and native cloud execution identifiers are removed only from declared public presentation copies. Numerical tables, curves, BAMs, native references, peaks/counts and plot files remain exact. Raw API/launch envelopes, prompts/reasoning/SSE, environment/credential dumps, caches and execution wrappers are excluded. Normalized task records expose actual immutable digests, versions and scientific commands without those private controls.

This is one small paired-end yeast design with two physical libraries and two technical runs each. It does not establish human, single-end, optional-mode, other-annotation or biological equivalence. The original local inputs and all raw evidence remain held until #473 is resolved.

This is written by an AI agent (model name unavailable) on Nico DeVeaux's behalf.

Nextflow lint covered 131 final-source files: zero errors and three existing warnings. Syntax validation is separate from scientific qualification.
