#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 poly_inputs.py
python3 prepare_poly_review.py
export NXF_BIN=AGENT_NEXTFLOW_HOME/framework/26.04.6/nextflow-26.04.6-dist.jar
export NXF_VER=26.04.6
export DOCKER_CONTEXT=colima
for case_dir in poly-nf-base poly-nf-current poly-nf-disabled; do
    (
        cd "$case_dir"
        export NXF_HOME="$PWD/nxf-home"
        /Users/nicholas.deveaux/.local/bin/nextflow run main.nf -ansi-log false > run.out 2>&1
    )
done
python3 assert_poly.py
