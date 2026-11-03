#!/usr/bin/env bash -C -e -u -o pipefail
plotFingerprint \
    --skipZeros --numberOfSamples 100 --labels SPT5_T0_REP2.mLb.clN control::SPT5_T0_REP2::SPT5_INPUT_REP2.mLb.clN \
     \
    --bamfiles SPT5_T0_REP2.mLb.clN.sorted.bam SPT5_INPUT_REP2.mLb.clN.sorted.bam \
    --plotFile SPT5_T0_REP2.mLb.clN.plotFingerprint.pdf \
    --outRawCounts SPT5_T0_REP2.mLb.clN.plotFingerprint.raw.txt \
    --outQualityMetrics SPT5_T0_REP2.mLb.clN.plotFingerprint.qcmetrics.txt \
    --numberOfProcessors 2
