include { PRESEQ_LCEXTRAP } from './module'
workflow { PRESEQ_LCEXTRAP(Channel.of([[id:'library', single_end:false],file('input.bam')])) }
