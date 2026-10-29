# Agreement with archived HIV BWA data

The new fixed BWA library-consensus matrix agrees exactly with the archived original dev matrix (`19f44e`): all 74,895 coordinate rows and all 299,580 sample/count cells match. The new unfixed matrix (`73155d`) independently agrees exactly with the archived PR448 matrix (`5caa50`). The strict comparator joins genomic coordinates and library names, rejecting duplicate keys and ambiguous sample columns.

The archived dev matrix compared with the new unfixed arm has 6,982 changed cells on shared coordinates, plus 5,299 archive-only and 5,339 new-unfixed-only intervals. The exact numeric recovery therefore reproduces both sides of the historical difference on full-input BWA data.

This compares the retained historical BWA matrices, not a newly executed immediate pre-448-parent workflow. Historical FASTQ byte identity is not established; headers, task metadata and all biological outputs are not asserted byte-identical. The separate resequencing study tests the Chromap library-ID correction directly.

See [full differences and file hashes](historical-comparison.json) and [reproduction script](reporting/historical_comparison.py). Run the script with --campaign-root, --evidence-repo, and --out, using the retained strict compare_campaign_outputs.py helper and the evidence repository’s pinned compare_featurecounts.py.
