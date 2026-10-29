include { PICARD_MERGESAMFILES as PICARD_MERGESAMFILES_LIBRARY } from "${WORKTREE_ROOT}/atacseq-pr448-proposed-fix/modules/nf-core/picard/mergesamfiles/main"
include { PICARD_MARKDUPLICATES } from "${WORKTREE_ROOT}/atacseq-pr448-proposed-fix/modules/nf-core/picard/markduplicates/main"
include { PICARD_ADDORREPLACEREADGROUPS } from "${WORKTREE_ROOT}/atacseq-pr448-proposed-fix/modules/nf-core/picard/addorreplacereadgroups/main"


workflow FASTQ_ALIGN_CHROMAP {
    take:
    bams
    reference
    main:
    PICARD_ADDORREPLACEREADGROUPS(bams, reference)
    ch_bam = PICARD_ADDORREPLACEREADGROUPS.out.bam
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
    bams = channel.of([1, 1], [1, 2], [2, 1], [2, 2]).map { replicate, lane ->
        [[id: "SAMPLE_A_REP${replicate}_T${lane}", single_end: false, read_group: 'unused'], file("${projectDir}/../../inputs/rep${replicate}_lane${lane}.bam")]
    }
    FASTQ_ALIGN_CHROMAP(bams, reference)
    ch_genome_bam = FASTQ_ALIGN_CHROMAP.out.bam
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
    MERGED_LIBRARY_MARKDUPLICATES_PICARD.out.metrics.view { meta, path -> "METRICS\t${meta.id}\t${path}" }
    MERGED_LIBRARY_MARKDUPLICATES_PICARD.out.bam.view { meta, path -> "OUTPUT\t${meta.id}\t${path}" }
}
workflow NFCORE_ATACSEQ { ATACSEQ() }
workflow { NFCORE_ATACSEQ() }
