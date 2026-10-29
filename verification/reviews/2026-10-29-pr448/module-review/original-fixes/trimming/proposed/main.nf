include { TRIMGALORE } from '${WORKTREE_ROOT}/atacseq-pr448-proposed-fix/modules/nf-core/trimgalore/main'
workflow {
    TRIMGALORE(channel.of([[id: 'poly', single_end: false], [file("${projectDir}/../inputs/poly_1.fastq.gz"), file("${projectDir}/../inputs/poly_2.fastq.gz")]]))
    TRIMGALORE.out.reads.view()
    TRIMGALORE.out.versions_trimgalore.map { process, tool, version -> "${tool}=${version}" }.collectFile(name: 'tool-version.txt', storeDir: projectDir, newLine: true)

}
