This is a selected public evidence package for independent grading of six existing PR448 audit lanes. `PUBLIC-MANIFEST.json` is the allowlist and records every retained file's original/public SHA256, byte counts and actual normalization rules. The package contains reports, observed outputs, commands, comparison code, source/container/input pins and small fixtures. It is not a complete standalone distribution of every reference, index or large BAM.

| Lane | Evidence and classification |
|---|---|
| alignment-peak | Actual BWA/Bowtie2/Chromap/MACS controls and pinned upstream/pipeline source. Expected metadata/reporting/format differences are separated from changed mappings. These are direct tool controls, not additional full pipeline runs. |
| samstats | Actual recorded SAMtools versions on two synthetic upstream fixtures; summary fields agree in this bounded control. No general unchanged-behavior proof. |
| picard-optical | Both tested Picard versions make the same duplicate decisions and report zero optical pairs for the boundary fixture expecting one. Shared/inherited behavior; not a newly introduced PR448 defect. |
| preseq-retry | Actual Nextflow source wrappers exercised with a fake argv-checking PRESEQ executable. The current wrapper loses original retry options and fails; append-based control preserves them. This is an argument/retry reproduction, not a scientific complexity estimate. |
| read-group-scope | Source/history evidence distinguishes inherited BWA/Bowtie2 technical-run LB values from PR448's newly added Chromap replacement step. It is not another duplicate-marking reproduction. |
| human-macs | One complete cleaned human library, fixed-BWA source, default broad/BAMPE/no-control. All30438broad peaks and noncomment XLS fields agree between3.0.1/3.0.4; gappedPeak fields7–8 change to zero. The3.0.4 replay agrees exactly with archived cloud outputs. Equality is at emitted precision, not internal floating-point or biological equivalence. |

Read each lane's `REPORT.md`, `SUMMARY.md` or `result.json` for actual limits and negative results. The human MACS64MiB attempt is explicitly invalid despite exit0: temporary-file I/O errors occurred. Its classification, execution record and logs remain; duplicate invalid peak files are omitted. The valid comparisons use the repeated512MiB pair. PRESEQ's28-byte `input.bam` files are declared stand-in text fixtures, not scientific BAM data.

Offline checks, executed on this staged public subset:

```sh
python3 -B verify_public.py
python3 -B alignment-peak/check.py
python3 -B verify_human_outputs.py
python3 -B -m unittest discover -s human-macs -p test_compare.py
```

The self-verifier checks the exact allowlist, hashes, size caps and known private/credential patterns, including bounded decoded gzip/BGZF and every ZIP/TAR member if present. Public `ngi-igenomes` reference and `nf-core-awsmegatests` test URIs in pinned nf-core source are explicitly permitted. This is a declared literal/format audit, not a universal proof concerning arbitrary encodings.

Local review/home/scratch paths and internal bucket references are replaced with symbolic markers. Scientific numbers, original source pins and hash values remain intact; JSON nonstring-token and SAM nonheader-byte preservation are checked where applicable. Original `ARTIFACTS.json`/`SAVED-EVIDENCE.json` records describe historical source capture and may mention omitted inputs; use `PUBLIC-MANIFEST.json` for this package's published bytes.

`EXTERNAL-INPUTS.json` identifies the omitted285036036-byte human BAM by exact workflow/case/member/SHA. The source archive transfer is in progress and its release is not yet publicly published; this is a retrieval identity, not a current public download link. Rebuildable mapper indexes and larger yeast references/BAMs are likewise not duplicated here; their pins remain in `alignment-peak/input-pins.json`.

Container and scientific argv records are retained. Historical run scripts contain normalized machine paths or require omitted inputs/indexes and cached images; their portability was not tested. To replay tools, first supply the exact pinned inputs and map symbolic paths into a fresh scratch directory, then use public pinned images. Do not run harnesses in the evidence directory: some refuse existing outputs or write generated files. No new scientific runs were performed to assemble this package. Proprietary Portal/billing material and historical GFF crash witnesses are outside this package's scope.
