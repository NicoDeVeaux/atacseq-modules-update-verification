# PR #448: Chromap library identity regression

Confirmed against nf-core/atacseq dev `73155d2b59d37f521e3f00228d559031d2e7847f`, comparing pre-PR `4177ea95c56e15fdbdc52f6e210c3329ff69167b` and merged `a51bee0178045b29cd9f034e58f4de6b80bc91db`.

`conf/modules.config:303` now assigns Chromap read groups `RGLB = meta.id`, including `_T1`, `_T2`, etc. Those are lane/resequencing identifiers for one library, as documented in `docs/usage.md:36` and `docs/usage.md:74`. The workflow subsequently strips `_Tn` before merging the BAMs (`workflows/atacseq.nf:246`), but BAM `LB` tags remain different. Picard therefore treats identical fragments in different runs as belonging to different libraries and does not mark the cross-run duplicates.

Run `./run.sh` from this directory. It generates two tiny aligned BAMs containing the same mapped read pair under different names, then runs actual pipeline Picard modules with the actual configuration and verbatim channel code for merging technical runs. Chromap alignment itself is replaced by those post-alignment BAMs. No cloud data or full pipeline run is used. The baseline BAMs have no `@RG` header or `RG:Z` record tag by construction. That models the historical Chromap 0.2.4 output: its [SAM writer](https://github.com/haowenz/chromap/blob/v0.2.4/src/mapping_writer.cc#L308-L354) emits only `@SQ` headers and `NM`/`MD` (optionally `CB`) tags, with no RG; the pre-PR module converts that SAM using `samtools view -bh` without adding read groups. The fetched upstream source is saved as `chromap-v0.2.4-mapping_writer.cc`, blob `2bb381ee7796977adaf077c0ad0547b590ef7c65`. No old Chromap executable was run in this test.

| Case | Read pairs | Duplicate pairs | Reads retained after duplicate filtering |
|---|---:|---:|---:|
| Actual pre-PR modules/config, Picard 3.1.1, no RG | 2 | 1 | 2 |
| Current modules/config, Picard 3.4.0, per-run LB | 2 | 0 | 4 |
| Current with `_Tn` removed from LB | 2 | 1 | 2 |

The `base-main.nf` imports the actual pre-PR MergeSamFiles and MarkDuplicates modules. `main.nf` imports current AddOrReplaceReadGroups, MergeSamFiles, and MarkDuplicates modules. The base profile maps the historical image name to an already cached Quay mirror of the same Picard version. Nextflow 26.10.2 is used. Every run exits zero. The all-selector configuration causes expected warnings for omitted pipeline processes; task cache persistence warnings occurred under this isolated runner, so the test uses fresh work and does not rely on resume.

The result is saved in `summary.json`; `check.py` checks both Picard metrics and actual BAM duplicate flags via `samtools view -c -F 0x400`. The correction is tested only in the reproduction profile. No source checkout is modified.

Suggested fix: keep each `RGID` distinct, but set `RGLB` to the library identity with `_Tn` removed, matching the existing `RGSM`. This bug already existed in BWA/Bowtie2 configurations; #448 newly introduces it to Chromap, which previously had no read groups. Do not describe the older aligners' behavior as a new #448 regression.

Current upstream `dev` was fetched again through the GitHub API: the relevant config blob is unchanged. `nf-core/modules` master still has the same optional read-group stage; caller-specific LB assignment lives in atacseq. Three issue-search phrasings found no matching issue; see `issue-searches.json`. This is a local review only.

Other inspected changes did not produce findings: updated aligner signatures agree with their callers; unified index outputs are joined by matching metadata; the new singleton fasta/FAI construction ends in `first()` and is reusable. A Nextflow counterexample attempt under `reference-broadcast-REFUTED/` exercises three samples through three consumers, including the BWA reference remapping; all nine expected executions occur. This does not validate all alignment/tool version changes or establish whole-pipeline equivalence.
