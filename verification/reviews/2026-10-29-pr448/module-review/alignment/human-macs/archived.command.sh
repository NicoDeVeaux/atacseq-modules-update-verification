#!/usr/bin/env bash -C -e -u -o pipefail
macs3 \
    callpeak \
    --keep-dup all --nomodel --broad --broad-cutoff 0.1 \
    --gsize 2701262066 \
    --format BAMPE \
    --name HIV_CD86HI_48H_REP1.mLb.clN \
    --treatment HIV_CD86HI_48H_REP1.mLb.clN.sorted.bam \

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
nxf_eval_cmd STDOUT STDERR bash -c "macs3 --version | sed -e 's/macs3 //'"
status=$?
if [ $status -eq 0 ]; then
  echo nxf_out_eval_33="$STDOUT" >> .command.env
  echo /nxf_out_eval_33/=exit:0 >> .command.env
else
  echo nxf_out_eval_33="$STDERR" >> .command.env
  echo /nxf_out_eval_33/=exit:$status >> .command.env
fi
