include { PICARD_ADDORREPLACEREADGROUPS } from "REVIEW_ROOT/source/modules/nf-core/picard/addorreplacereadgroups/main"
include { PICARD_MERGESAMFILES as PICARD_MERGESAMFILES_LIBRARY } from "REVIEW_ROOT/source/modules/nf-core/picard/mergesamfiles/main"
include { PICARD_MARKDUPLICATES } from "REVIEW_ROOT/source/modules/nf-core/picard/markduplicates/main"

workflow FASTQ_ALIGN_CHROMAP {
    take:
    bams
    reference
    main:
    if (params.case != 'old') {
        PICARD_ADDORREPLACEREADGROUPS(bams, reference)
        ch_bam = PICARD_ADDORREPLACEREADGROUPS.out.bam
    } else {
        ch_bam = bams
    }
    emit:
    bam = ch_bam
}

workflow MERGED_LIBRARY_MARKDUPLICATES_PICARD {
    take:
    bams
    reference
    main:
    PICARD_MARKDUPLICATES(bams, reference)
    emit:
    bam = PICARD_MARKDUPLICATES.out.bam
    metrics = PICARD_MARKDUPLICATES.out.metrics
}

workflow ATACSEQ {
    main:
    reference = channel.value([[:], [], []])
    bams = channel.of(1, 2).map { lane -> [[id: "SAMPLE_A_REP1_T${lane}", single_end: false, read_group: 'unused'], file("${projectDir}/inputs/lane${lane}.bam")] }
    FASTQ_ALIGN_CHROMAP(bams, reference)
    ch_genome_bam = FASTQ_ALIGN_CHROMAP.out.bam
    // Verbatim library-merge wiring from workflows/atacseq.nf.
    ch_genome_bam
        .map {
            meta, bam ->
                def meta_clone = meta.clone()
                meta_clone.remove('read_group')
                meta_clone.id = meta_clone.id - ~/_T\d+$/
                [ meta_clone, bam ]
        }
        .groupTuple(by: [0])
        .map {
            meta, bam ->
                [ meta, bam.flatten() ]
        }
        .set { ch_sort_bam }
    PICARD_MERGESAMFILES_LIBRARY(ch_sort_bam)
    MERGED_LIBRARY_MARKDUPLICATES_PICARD(PICARD_MERGESAMFILES_LIBRARY.out.bam, reference)
    MERGED_LIBRARY_MARKDUPLICATES_PICARD.out.metrics.view { meta, path -> "METRICS ${path}" }
    MERGED_LIBRARY_MARKDUPLICATES_PICARD.out.bam.view { meta, path -> "OUTPUT ${path}" }
}
workflow NFCORE_ATACSEQ { ATACSEQ() }
workflow { NFCORE_ATACSEQ() }
