# Public HIV report supplement

The two ordered compressed archive parts preserve 172 decoded-audited outputs from the four historical HIV workflows: 84 HTML reports, 64 FastQC ZIPs, 16 RData files and eight RDS files. The compressed stream is 53,909,954 bytes; the expanded payload size is 98,820,013 bytes. TAR names retain `files/CASE/relative/output/path`.

This is a partial supplement to the existing scientific text/execution captures. It does not contain the complete 2,686-file output archive, BAMs, bigWigs or reference indexes. Fixed workflows used a9b588; unfixed workflows used 73155d. Exact source commits and workflow IDs are in `manifest.json`. These observations are not relabeled as testing later fixes.

The public inputs are SRR8508547, SRR8508548, SRR8508553 and SRR8508554. Their ENA URLs/checksums and the matched 87,089,251 input-pair counts are documented in the parent bundle's `hiv/results/hiv-input-provenance.json`. Matching historical counts does not establish historical FASTQ byte identity.

## Verify downloaded bytes

Use Python 3.9+ and the standard library:

```sh
python3 -B verify.py
python3 -B verify.py --self-test
```

The streaming verifier checks the exact part inventory, each part and concatenated gzip hash, the member-manifest hash, normalized regular TAR members, exact member inventory, sizes and SHA-256 hashes. It does not extract, execute artifacts or contact a service. The self-test uses tiny temporary fixtures to check corruption, missing/extra members, duplicate names, symlinks, unexpected parts and a wrong manifest pin; distributed files remain unchanged. Pass `--archive-manifest-sha256 FULL_SHA256` when a trusted parent checksum is available. Integrity is not independent authentication of the manifests or scientific validation.

## Single-file download mirror

The planned [report-object supplement release](https://github.com/NicoDeVeaux/atacseq-modules-update-verification/releases/tag/pr448-hiv-report-objects-2026-11-02) provides the same compressed bytes as one [hiv-decoded-report-supplement.tar.gz](https://github.com/NicoDeVeaux/atacseq-modules-update-verification/releases/download/pr448-hiv-report-objects-2026-11-02/hiv-decoded-report-supplement.tar.gz) asset, alongside `archive.json`, `manifest.json` and `verify.py`. This mirror is separate from the unfinished full-output archive. The links become downloadable when that supplement release is published; packaging alone does not establish their availability.

Download those four files into a new directory through the release page, or optionally use GitHub CLI:

```sh
gh release download pr448-hiv-report-objects-2026-11-02 \
  --repo NicoDeVeaux/atacseq-modules-update-verification \
  --pattern hiv-decoded-report-supplement.tar.gz \
  --pattern archive.json --pattern manifest.json --pattern verify.py
python3 -B verify.py --archive-file hiv-decoded-report-supplement.tar.gz
```

Single-file mode verifies the complete compressed size/hash, pinned member manifest and the same streaming exact TAR member checks. It does not require the split parts. The complete file is a release asset; Git retains only the two split parts. This release contains report objects from all four cases, not all output files from those cases.

## Extract the verified split archive

After successful verification, use a new empty extraction directory and the order in `archive.json`:

```sh
mkdir unpacked
cat parts/hiv-decoded-report-supplement.tar.gz.part-* | tar -xzf - -C unpacked
```

Individual parts are fragments of one gzip stream. All parts are required. Extraction needs about 99 MB plus filesystem overhead. Inspect the verified HTML reports as downloaded files; serialized R objects and ZIPs are preserved without loading or extracting them during verification.

Original and distributed content identities are separate. Existing sealed payload and audit-report hashes were reverified during packaging; decoded audits and scientific workflows were not rerun. Static HTML audits decoded embedded payloads without executing artifact JavaScript. ZIP audits covered members and nested supported formats. R parser audits covered reachable numeric arrays and masks without running R code. Per-file transformations, numeric-preservation evidence and audit limits remain explicit. Audit-report hashes identify existing audit records; private source reports are not redistributed here.

Private local paths, source storage locators, ETags, credentials, signed URLs and launch payloads are excluded from the public manifest. Public study labels and scientific output names are preserved. The source pipeline's MIT license and copyright remain in the parent bundle. This supplement adds generated outputs and existing report assets, with their upstream notices, rather than tool binaries or containers.

This is written by an AI agent (model name unavailable) on Nico DeVeaux's behalf.
