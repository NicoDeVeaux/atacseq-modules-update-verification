The complete public PR448 resequencing control is stored in ten ordered archive parts, rather than 4,565 loose Git paths. All original files are preserved. The readable scientific reports and selected source/input/parameter receipts are beside the parts; the entire portable workflow and original evidence are available after unpacking.

The joined archive is **431,843,357 bytes** (411.84 MiB), SHA256 prefix `03a1b1` (full value in `parts-manifest.json`). Each part is at most **43 MiB**. `parts-manifest.json` specifies the exact order, sizes and SHA256 values; `archive-members.jsonl` indexes every archived directory/file and each file’s checksum. `SOURCE-PACKAGE-ARTIFACTS.sha256` identifies the unchanged source package manifest.

Verify the parts and every member without writing an extracted copy:

```sh
python3 verify_parts.py
```

This uses Python 3.9+ standard library only. It checks part identity/order, the concatenated full gzip archive, all 4,565 file contents, 1,140 directories, normalized safe tar metadata and the exact original package manifest. It neither launches workflows nor contacts a service.

To unpack after successful verification:

```sh
mkdir -p unpacked
cat parts/pr448-resequencing-control.tar.gz.part-* | tar -xzf - -C unpacked
(cd unpacked && shasum -a 256 -c ../SOURCE-PACKAGE-ARTIFACTS.sha256)
cd unpacked/pr448-resequencing-control
sh check.sh
```

The archive contains one relative root, `pr448-resequencing-control/`; it has no absolute/parent-traversal paths, symlinks, devices, special permissions or stored usernames. Extraction requires about 618MB for file contents plus filesystem overhead. The optional offline `check.sh` reads the included actual public FASTQs and evidence and runs 18existing parser/comparator tests. It does not run Nextflow or a scientific tool. Follow the unpacked README for explicit future workflow replay commands.

The scientific control includes 8exact public FASTQ prefixes (250,000 actual pairs/run), 4exact shared-alignment BAMs, 6final cleaned BAMs, compressed matching sacCer3 FASTA/GTF, source archives/licenses, all 469scientific task evidence sets, reports, counts, peaks, metrics, primary metadata and the one-count residual trace. Raw instrument reads remain 101bases; effective genome sizing uses the supported 100-base bin and recorded MACS3 size 11,777,680.

The original bundle’s public-data/path/embedded MultiQC checks passed and its source snapshot was unchanged during distribution. Raw private Co-Scientist reasoning/SSE, prompts/tool inputs, environment/cache/wrapper content and the separate B1 archive are excluded. No new payload material was added to the scientific archive.

The source package is preserved byte-for-byte; its original report’s 20-test statement is historical. Eighteen test methods were located and passed. The archived original numbers remain unchanged; an offline recomputation has six Pearson last-bit differences (at most 1.45e-15), with all counts/coordinates identical. These limitations are explicit in the unpacked README/derived manifest.

`reports/` contains exact copied public reports. Their relative links refer to the original paths inside the unpacked package. `review/` contains exact selected source/input/completion/parameter receipts. `loose-review-files.json` records those copies’ source paths/checksums.

The unsharded `.tar.gz` and `build_distribution.py` are local staging files and must not be added to the branch. Publish only `publish-files.json`: ten parts plus the small verification/manifests/reports/selected text. No release or remote publication has occurred, and no remote asset URL is claimed. A release mirror can later use the same full-archive checksum if separately authorized.
