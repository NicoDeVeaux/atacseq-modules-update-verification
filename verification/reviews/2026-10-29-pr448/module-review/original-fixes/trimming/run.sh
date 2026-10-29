#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
phase="${1:?Use baseline or proposed SOURCE}"
case "$phase" in
    baseline)
        python3 prepare.py baseline
        cases=(baseline negative-2.1)
        ;;
    proposed)
        source_path="${2:?Select the proposed pipeline source explicitly}"
        python3 prepare.py proposed --source "$source_path"
        cases=(proposed)
        ;;
    *) exit 2 ;;
esac
export NXF_BIN=${AGENT_NEXTFLOW}/framework/26.04.6/nextflow-26.04.6-dist.jar
export NXF_VER=26.04.6
export DOCKER_CONTEXT=colima
for case_dir in "${cases[@]}"; do
    (
        cd "$case_dir"
        export NXF_HOME="$PWD/nxf-home"
        ${HOME}/.local/bin/nextflow run main.nf -ansi-log false > run.out 2>&1
    )
done
python3 assert_results.py "$phase"
