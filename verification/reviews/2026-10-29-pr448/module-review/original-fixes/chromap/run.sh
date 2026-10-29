#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
case_name="${1:-baseline}"
case "$case_name" in baseline|proposed) ;; *) exit 2 ;; esac
shift || true
python3 make_inputs.py
for replicate in 1 2; do
  for lane in 1 2; do
    docker --context colima run --rm -v "$PWD/inputs:/data" -w /data \
      community.wave.seqera.io/library/htslib_samtools:1.23.1--5b6bb4ede7e612e5 \
      samtools view -b -o "rep${replicate}_lane${lane}.bam" "rep${replicate}_lane${lane}.sam"
  done
done
python3 prepare.py "$case_name" "$@"
export NXF_HOME="$PWD/.nxf-home"
export NXF_OFFLINE=true
export NXF_ANSI_LOG=false
export DOCKER_HOST=unix://${HOME}/.colima/default/docker.sock
cd "runs/$case_name"
java -jar ${AGENT_NEXTFLOW}/framework/26.10.2/nextflow-26.10.2-dist.jar -log nextflow.log run main.nf -work-dir work > run.out 2>&1
cd ../..
python3 check.py "$case_name"
