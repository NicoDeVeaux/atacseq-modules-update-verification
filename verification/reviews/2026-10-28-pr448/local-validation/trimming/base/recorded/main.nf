include { TRIMGALORE } from '../../base/modules/nf-core/trimgalore/main'
workflow {
    TRIMGALORE(channel.of([[id: 'poly', single_end: false], [file("${projectDir}/../poly-inputs/poly_1.fastq.gz"), file("${projectDir}/../poly-inputs/poly_2.fastq.gz")]]))
    TRIMGALORE.out.reads.view()
}
