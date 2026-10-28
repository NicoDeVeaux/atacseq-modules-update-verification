#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
review_root="$PWD"
review_jar=AGENT_NEXTFLOW_HOME/framework/26.10.2/nextflow-26.10.2-dist.jar
export NXF_HOME="$review_root/.nxf-home"
export NXF_OFFLINE=true
export NXF_ANSI_LOG=false
export DOCKER_HOST=unix:///Users/nicholas.deveaux/.colima/default/docker.sock
python3 generate_inputs.py
for lane in 1 2; do
  docker --context colima run --rm -v "$review_root/inputs:/data" -w /data \
    community.wave.seqera.io/library/htslib_samtools:1.23.1--5b6bb4ede7e612e5 \
    samtools view -b -o "lane${lane}.bam" "lane${lane}.sam"
done
java -jar "$review_jar" -C base.config -log base.nextflow.log run base-main.nf --case old -profile old -work-dir work-base > base.run.out 2>&1
java -jar "$review_jar" -log current.nextflow.log run main.nf --case current -work-dir work-current > current.run.out 2>&1
java -jar "$review_jar" -log fixed.nextflow.log run main.nf --case fixed -profile fixed -work-dir work-fixed > fixed.run.out 2>&1
python3 check.py
