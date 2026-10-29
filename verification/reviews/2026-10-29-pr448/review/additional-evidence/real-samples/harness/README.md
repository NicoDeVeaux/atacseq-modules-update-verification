# Real technical-run validation harness

This prepares two complementary tests without changing pipeline checkouts:

1. `raw/{base,unfixed,fixed}` starts from real paired FASTQ records and runs each
   source's actual trimming subworkflow, Chromap index/module/subworkflow,
   verbatim technical-run merge wiring, and Picard MergeSamFiles/MarkDuplicates.
2. `shared/{base,unfixed,fixed}` gives all three actual Picard chains the **same**
   pre-read-group Chromap BAMs published by `raw/unfixed/raw_chromap`. Each chain
   uses its own actual sorting/read-group and Picard modules. This holds the
   aligned input constant when isolating the library-tag correction.

The first test changes Trim Galore, Chromap and Picard versions between historical
and current sources. Do not promise full base/fixed alignment identity. In the
second test, unfixed/fixed use the same actual modules except their read-group
configuration; baseline retains historical Picard/no-RG behaviour. Compare
duplicate counts and retained read/fragment sets, allowing duplicate-keeper tie
differences for historical Picard. A genuine library must have observable
cross-run duplicate loci for this dataset to demonstrate the defect.

Prepare after the parent prefix downloader produces local inputs:

```bash
python3 prepare.py --samples /path/to/selected-inputs.json \
  --fasta LOCAL_TMP/pr448-realdata-reference/sacCer3.fa --out /path/to/prepared
bash run_case.sh /path/to/prepared raw unfixed
bash run_case.sh /path/to/prepared raw base
bash run_case.sh /path/to/prepared raw fixed
for case in base unfixed fixed; do
  bash run_case.sh /path/to/prepared shared "$case"
done
```

Input JSON accepts `{"samples": [{"id": "GSM6208857_T1", "read1": "/local/R1.fastq.gz",
"read2": "/local/R2.fastq.gz"}, ...]}`. IDs end in `_Tn`; only that suffix is removed
to identify the biological library, preserving distinct biological replicates.
The parent helper selects the first N genuine paired records without duplication;
this harness does not synthesise, concatenate or duplicate reads. Dataset/library
metadata must establish same physical-library resequencing and correct reference
assembly. The default minimum trimmed count is the pipeline's 10,000; use
`--min-trimmed-reads 0` only for a labelled 1,000-pair smoke run. Optional
`--skip-trimming` isolates raw-mapping effects while keeping all three arms alike.

`OUTPUT\tID\tBAM` identifies marked BAMs; `METRICS\tID\tPATH` identifies actual
Picard metrics; `ALIGNED\ttechnicalID\tBAM` identifies sorted per-run alignments.
Raw Chromap BAMs before RG replacement are copied under each raw case's
`raw_chromap/`. The harness stops at duplicate marking: it does not claim the
full pipeline's blacklist/mitochondrial/orphan filtering, peaks or DESeq2 analysis.
The independent analyser can count reads retained under an explicitly stated
duplicate-flag filter. No `FILTERED` record is emitted.

Sources, module hashes, exact copied merge code and registry-only overrides are
recorded per case in `source-used.json`; `inputs-provenance.json` records the input
manifest/reference hashes. Legacy `biocontainers/` references are mapped to the
Quay mirror with identical image names/tags. Small-reference runs request two
CPUs/4 GB per task with at most two local tasks. The source small-genome index is
built separately per Chromap version; unfixed/fixed therefore share the version,
not an assumed cross-version index format. All command logs/work are retained.

No full data run has been performed merely by preparing these files. The actual
source snapshots remain unmodified. No cloud operation or publication is part of
the harness.
