#!/bin/bash -ue
picard \
    -Xmx819M \
    MergeSamFiles \
    --SORT_ORDER coordinate --VALIDATION_STRINGENCY LENIENT --TMP_DIR tmp \
    --INPUT rep2_lane1.bam --INPUT rep2_lane2.bam \
    --OUTPUT SAMPLE_A_REP2.mLb.sorted.bam
cat <<-END_VERSIONS > versions.yml
"NFCORE_ATACSEQ:ATACSEQ:PICARD_MERGESAMFILES_LIBRARY":
    picard: $( echo $(picard MergeSamFiles --version 2>&1) | grep -o 'Version:.*' | cut -f2- -d:)
END_VERSIONS
