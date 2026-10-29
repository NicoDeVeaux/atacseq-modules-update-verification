# PR448 module-version inventory

Pinned comparison: actual first parent `4177ea` → merge `a51bee`. Merge ancestry was checked.

- 36 nf-core modules: 33 updated, 2 added, 1 removed (`custom/getchromsizes`).
- 7 nf-core subworkflows, 18 local modules, 9 local subworkflows.
- 267 changed files covered; zero unassigned module/subworkflow files.

Both modules.json files use the same repos → modules/subworkflows → nf-core layout. Old/new lock entries, upstream module SHAs, local patch paths, exact source declarations and source URLs are retained in inventory.json. inventory.tsv is the flat view; tool-map.json groups tool families and every declared Conda package.

These are declared pins, not runtime binary measurements. Container references, image tags/digests and Conda declarations are separate. Opaque Wave/mulled image contents and unpinned R environments are not guessed. Static reachability means a possible include path, not an observed task execution.

| nf-core family | Old primary Conda declaration | At-merge primary Conda declaration | Metadata/citation URL |
|---|---|---|---|
| ataqv | bioconda::ataqv=1.3.1 | bioconda::ataqv=1.3.1 | https://github.com/ParkerLab/ataqv |
| bowtie2 | bioconda::bowtie2=2.4.4; bioconda::bowtie2=2.5.2 | bioconda::bowtie2=2.5.4 | http://bowtie-bio.sourceforge.net/bowtie2/index.shtml |
| bwa | bioconda::bwa=0.7.19; bwa=0.7.17 | bioconda::bwa=0.7.19 | http://bio-bwa.sourceforge.net/ |
| chromap | bioconda::chromap=0.2.4 | bioconda::chromap=0.3.2 | https://github.com/haowenz/chromap |
| custom |  |  | http://www.htslib.org/ |
| deeptools | bioconda::deeptools=3.5.5 | bioconda::deeptools=3.5.6 | https://deeptools.readthedocs.io/en/develop/content/tools/alignmentSieve.html |
| gffread | bioconda::gffread=0.12.1 | bioconda::gffread=0.12.7 | http://ccb.jhu.edu/software/stringtie/gff.shtml#gffread |
| gunzip |  | conda-forge::gzip=1.13 | https://www.gnu.org/software/gzip/manual/gzip.html |
| homer | bioconda::homer=4.11 | bioconda::homer=4.11 | http://homer.ucsd.edu/homer/ |
| khmer | bioconda::khmer=3.0.0a3 | bioconda::khmer=3.0.0a3 | https://github.com/dib-lab/khmer |
| macs3 | bioconda::macs3=3.0.1 | bioconda::macs3=3.0.4 | https://macs3-project.github.io/MACS/ |
| multiqc | bioconda::multiqc=1.34 | bioconda::multiqc=1.35 | https://multiqc.info/ |
| picard | bioconda::picard=3.0.0; bioconda::picard=3.1.1; bioconda::picard=3.4.0 | bioconda::picard=3.4.0 | http://broadinstitute.github.io/picard |
| preseq | bioconda::preseq=3.1.2 | bioconda::preseq=3.2.0 | http://smithlabresearch.org/software/preseq/ |
| samtools | bioconda::samtools=1.19.2 | bioconda::samtools=1.23.1; bioconda::samtools=1.24 | http://www.htslib.org/ |
| subread | bioconda::subread=2.0.1 | bioconda::subread=2.0.1 | http://bioinf.wehi.edu.au/featureCounts/ |
| trimgalore | bioconda::trim-galore=0.6.10 | bioconda::trim-galore=2.1.0 | https://github.com/FelixKrueger/TrimGalore/blob/master/Docs/Trim_Galore_User_Guide.md |
| ucsc | bioconda::ucsc-bedgraphtobigwig=445 | bioconda::ucsc-bedgraphtobigwig=482 | http://hgdownload.cse.ucsc.edu/admin/exe/ |
| umitools | bioconda::umi_tools=1.1.6 | bioconda::umi_tools=1.1.6 | https://github.com/pysam-developers/pysam |
| untar | conda-forge::tar=1.34 | conda-forge::tar=1.34 | https://www.gnu.org/software/tar/manual/ |

Notable boundaries:

- nf-core MultiQC 1.34 → 1.35 was updated but is not reachable from pipeline main. The executing local MultiQC remains 1.13; its wrapper changed.
- Subread remains pinned at 2.0.1, with a recorded local patch. A module revision update is not a Subread upgrade.
- SAMtools/HTSlib declarations vary by process: faidx uses 1.23.1, standalone stats/index/sort modules use 1.24; aligner bundles carry 1.21, 1.22.1 or 1.23.1.
- Added modules: picard/addorreplacereadgroups and samtools/faidx. Subworkflows have no direct tool/container pins; their called modules are inventoried individually.
- Local module changes include conversion from versions.yml output to version topics. Their declared tool bindings are retained independently from nf-core modules.

No upstream bug conclusions are made by this inventory. No proposed fix, cloud run or upstream repository was changed.
