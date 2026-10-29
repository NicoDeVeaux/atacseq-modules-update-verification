#!/bin/bash -ue
picard \
    -Xmx819M \
    MarkDuplicates \
    --ASSUME_SORTED true --REMOVE_DUPLICATES false --VALIDATION_STRINGENCY LENIENT --TMP_DIR tmp \
    --INPUT SAMPLE_A_REP1.mLb.sorted.bam \
    --OUTPUT SAMPLE_A_REP1.mLb.mkD.sorted.bam \
     \
    --METRICS_FILE SAMPLE_A_REP1.mLb.mkD.sorted.MarkDuplicates.metrics.txt

cat <<-END_VERSIONS > versions.yml
"NFCORE_ATACSEQ:ATACSEQ:MERGED_LIBRARY_MARKDUPLICATES_PICARD:PICARD_MARKDUPLICATES":
    picard: $(echo $(picard MarkDuplicates --version 2>&1) | grep -o 'Version:.*' | cut -f2- -d:)
END_VERSIONS
