#!/bin/bash -ue
preseq \
    lc_extrap \
    -verbose -bam -seed 1 \
    -pe \
    -output library.lc_extrap.txt \
    input.bam
cp .command.err library.command.log

cat <<-END_VERSIONS > versions.yml
"PRESEQ_LCEXTRAP":
    preseq: $(echo $(preseq 2>&1) | sed 's/^.*Version: //; s/Usage:.*$//')
END_VERSIONS
