#!/usr/bin/env bash
# Fetch the original-paper ATAC-seq peak set (GSE125918 Table S3) and regenerate
# the GRCh38 BED used by the overlap analysis.
#
# The raw .gz (~15 MB) and the normalized TSV (~33 MB) are NOT committed to this
# repo (see .gitignore); this script reproduces them. The derived
# paper_peaks.GRCh38.bed IS committed so the overlap runs offline out of the box.
#
# Provenance:
#   Study SRP182967 -> GEO GSE125918 (ATAC-seq) / GSE125919 (SuperSeries)
#   Johnson, De Veaux et al., Cell Reports 2020; PMID 31968263
#   Gold-standard peak set: 87,681 Peakdeck peaks.
#
# Genome build: GRCh38/hg38 (NOT hg19). Verified from coordinates -- chr20's max
# peak end (64,286,330) exceeds hg19 chr20 length (63,025,520) but fits hg38
# chr20 (64,444,167). GEO lists "Genome_build: hg19; hg38"; this table is hg38.
# Therefore NO liftOver is required to compare against GRCh38 pipeline output.
#
# Usage:  bash verification/scripts/fetch_paper_peaks.sh
# Writes: verification/overlap/data/paper_original/{*.txt.gz, S3_normalized.tsv, paper_peaks.GRCh38.bed}
set -euo pipefail

OUTDIR="verification/overlap/data/paper_original"
URL="https://ftp.ncbi.nlm.nih.gov/geo/series/GSE125nnn/GSE125918/suppl/GSE125918_Table_S3_ATAC_peak_RLOG_counts.txt.gz"
GZ="$OUTDIR/GSE125918_Table_S3_ATAC_peak_RLOG_counts.txt.gz"
TSV="$OUTDIR/S3_normalized.tsv"
BED="$OUTDIR/paper_peaks.GRCh38.bed"

mkdir -p "$OUTDIR"

echo "[1/3] downloading $URL"
curl -fsSL -o "$GZ" "$URL"

# The file uses legacy \r (carriage-return) line endings; normalize to \n.
echo "[2/3] normalizing line endings -> $TSV"
gzcat "$GZ" 2>/dev/null | tr '\r' '\n' > "$TSV" || zcat "$GZ" | tr '\r' '\n' > "$TSV"

# Emit a 4-col BED (chrom, start, end, peak). Skip the header row.
echo "[3/3] writing $BED"
tail -n +2 "$TSV" | awk -F'\t' 'BEGIN{OFS="\t"} $2 ~ /^[0-9]+$/ && $3 ~ /^[0-9]+$/ {print $1,$2,$3,$4}' > "$BED"

echo "done: $(grep -c . "$BED") peaks -> $BED"
