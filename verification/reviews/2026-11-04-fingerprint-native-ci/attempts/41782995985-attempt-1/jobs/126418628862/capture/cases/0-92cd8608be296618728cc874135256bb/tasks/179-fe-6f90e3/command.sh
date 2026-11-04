#!/usr/bin/env bash -C -e -u -o pipefail
plotFingerprint \
    --skipZeros --numberOfSamples 100 --labels OSMOTIC_STRESS_T0_PE_REP1.mLb.clN \
     \
    --bamfiles OSMOTIC_STRESS_T0_PE_REP1.mLb.clN.sorted.bam \
    --plotFile OSMOTIC_STRESS_T0_PE_REP1.mLb.clN.plotFingerprint.pdf \
    --outRawCounts OSMOTIC_STRESS_T0_PE_REP1.mLb.clN.plotFingerprint.raw.txt \
    --outQualityMetrics OSMOTIC_STRESS_T0_PE_REP1.mLb.clN.plotFingerprint.qcmetrics.txt \
    --numberOfProcessors 2

# capture process environment
set +u
set +e
cd "$NXF_TASK_WORKDIR"

nxf_eval_cmd() {
    {
        IFS=$'\n' read -r -d '' "${1}";
        IFS=$'\n' read -r -d '' "${2}";
        (IFS=$'\n' read -r -d '' _ERRNO_; return ${_ERRNO_});
    } < <((printf '\0%s\0%d\0' "$(((({ shift 2; "${@}"; echo "${?}" 1>&3-; } | tr -d '\0' 1>&4-) 4>&2- 2>&1- | tr -d '\0' 1>&4-) 3>&1- | exit "$(cat)") 4>&1-)" "${?}" 1>&2) 2>&1)
}

echo '' > .command.env
#
nxf_eval_cmd STDOUT STDERR bash -c "plotFingerprint --version | sed \"s/plotFingerprint //g\""
status=$?
if [ $status -eq 0 ]; then
  echo nxf_out_eval_46="$STDOUT" >> .command.env
  echo /nxf_out_eval_46/=exit:0 >> .command.env
else
  echo nxf_out_eval_46="$STDERR" >> .command.env
  echo /nxf_out_eval_46/=exit:$status >> .command.env
fi
