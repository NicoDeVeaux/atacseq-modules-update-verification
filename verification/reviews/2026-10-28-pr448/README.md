# PR #448 correctness review — 2026-10-28

Original Co-Scientist run records and retained independent local validation for
[nf-core/atacseq #448](https://github.com/nf-core/atacseq/pull/448).
Reviewed revisions: pre-merge `4177ea`, merge `a51bee`, then-current dev `73155d`.
Full identities and original session/run provenance are in [provenance.json](provenance.json).

This review is separate from this repository's historical AWS A/B comparisons.
It contains focused trimming and duplicate-marking tests, not another full
biological workflow run.

## Evidence boundary

The original hosted Co-Scientist session's tool commands and outputs were
downloaded through authenticated Portal history. **Its final cleanup deleted
the temporary FASTQs, BAMs, raw log files and tool environments.** The original
working files are unavailable; the [cleanup command](coscientist/cleanup/tool-38/command.txt)
and [output](coscientist/cleanup/tool-38/stdout.txt) record why.

The `coscientist/` files below are authentic recorded command/output excerpts,
not reconstructed files or a new run. Each record contains the exact
`command.txt`, `raw-tool-output.json`, decoded `stdout.txt`/`stderr.txt`,
and tool identity/exit-code `record.json`. JSON fields were extracted without
changing their values. Reasoning, full conversation, account/profile metadata
and credentials are excluded. Selected original records required no redaction.
[Export manifest](coscientist/export-manifest.json).

[local-validation/](local-validation/) separately contains retained independent
Nextflow/container test inputs, command scripts, outputs, metrics and results.
Its file manifest records original/published hashes and any local-path
normalization. It must not be described as the original Co-Scientist sandbox.

## Trim Galore: original public-data experiment

Co-Scientist ran 0.6.10 and 2.1.0 on the same public paired `SRR1822154` data:

| Record | Original evidence |
|---|---|
| [28](coscientist/trimgalore/tool-28/) | Tool environment setup and executable paths |
| [29 command](coscientist/trimgalore/tool-29/command.txt), [output](coscientist/trimgalore/tool-29/stdout.txt) | Public input URLs, actual trimming commands, both runs reporting exit 0 |
| [30 command](coscientist/trimgalore/tool-30/command.txt), [output](coscientist/trimgalore/tool-30/stdout.txt) | MD5s, retained counts, autodetection, poly-C clipping and literal before/after R2 sequence excerpts |
| [31 output](coscientist/trimgalore/tool-31/stdout.txt) | Paired/single-end report-parser checks |

The original recorded run retained 99,710 pairs with 0.6.10 and 99,681 with
2.1.0. The latter reports 2,203 R2 reads with poly-C trimmed. The sequence
excerpts show leading C bases removed from R2. These are original recorded
observations, not regenerated outputs.

The [upstream defect](https://github.com/FelixKrueger/TrimGalore/pull/322) is fixed
in 2.3.0. #448 imported 2.1.0. The independent local fixture uses the real
Nextflow modules and each revision's pipeline arguments: all 100 pairs survive,
but the current default removes 20 leading C bases per R2. Adding
`--no_poly_g` restores both mates' baseline sequences.

## Chromap/Picard: original duplicate-marking experiment

The original test starts with synthetic post-alignment SAMs containing
coordinate-identical pairs. It does not execute Chromap alignment.

| Record | Original evidence |
|---|---|
| [34 command](coscientist/chromap-picard/tool-34/command.txt), [output](coscientist/chromap-picard/tool-34/stdout.txt) | Full SAM generator, merge/mark commands, zero duplicates with per-run library tags |
| [35 output](coscientist/chromap-picard/tool-35/stdout.txt) | Picard 3.4.0 exception with no read groups |
| [36 command](coscientist/chromap-picard/tool-36/command.txt), [output](coscientist/chromap-picard/tool-36/stdout.txt) | Picard 3.1.1 baseline: one duplicate pair/two duplicate-flagged reads |

**Exit-code limitation:** tool 34's no-read-group Picard command fails although
its outer shell exits 0; stderr is preserved. Tool 35 confirms the exception.
A shell-wrapper status of 0 does not mean all nested commands succeeded.

Independent validation with actual base/current Nextflow Picard modules,
pipeline configuration and verbatim library-merge wiring confirms:

| Case | Duplicate pairs | Reads after duplicate-flag filtering |
|---|---:|---:|
| Before #448 | 1 of 2 | 2 |
| Current per-run library tags | 0 of 2 | 4 |
| Current with shared library identity | 1 of 2 | 2 |

Keep distinct run `RGID` values but remove `_T<n>` from `RGLB` for the
documented same-library resequencing case. Picard is following the library tags;
this is an atacseq configuration issue.

## Other follow-up and validation

The workflow-version omission already has an open fix in
[PR #469](https://github.com/nf-core/atacseq/pull/469), tracked by
[#470](https://github.com/nf-core/atacseq/issues/470).

This bundle does not quantify downstream biological peak/count effects.
It preserves failed commands as well as successful evidence. The original
agent run is complete; retrieval did not start another paid turn.

Verify from the repository root:

```bash
shasum -a 256 -c verification/reviews/2026-10-28-pr448/sha256sums.txt
```

The scoped `.gitattributes` preserves original output whitespace, including
trailing empty TSV fields and blank lines; those bytes are not reformatted.

This is written by GPT-6 (Codex) on Nico DeVeaux’s behalf.
