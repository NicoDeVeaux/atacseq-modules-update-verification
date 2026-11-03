Reporting data integrity passed. Both fingerprint TXT files are byte-identical across five accepted scopes: actual NF25/F723 output, its reversed-input replay, actual NF26/F532 output, and F723 forward/reversed report replays on that NF26 context. All eight series and all 782 numeric points match the installed, unmodified MultiQC 1.13 parser. Counts MD5: `fdc55f`; plot MD5: `970eea`. Full hashes and file receipts are in TWO-ENGINE-QUALIFICATION.json.

Nextflow 25.10.4 literally ran the final F723 source (map `a22dc3`). Nextflow 26.10.5 literally ran F532 (map `55a642`), followed by actual F723 report-only replays with the complete retained context. This does not claim a literal full NF26/F723 workflow. Both normal Nextflow resumes had 253 successful logical tasks: 88 cached and 165 newly completed. The five reporting roles freshly completed on each engine.

NF25 also retained one failed plotHeatmap attempt, exit 139, followed by a successful built-in retry. Its cause is unestablished. Failed command, stderr, exit and trace receipts are preserved under failed-attempts and TASK-ATTEMPTS.json. No source, retry policy or dependency override was used.

All 14 scientific input hashes and exact task/mate roles match the immutable old binding. All four treatment/control BAM pairings match; producer command scripts, complete literal raw-row multisets and all quality nonlabel fields agree across engines. The prior NF25 reporting bridge also retains identical per-role numeric curves, raw-row multisets and quality fields despite the intended control-label scheme change.

All original source, snapshots, cached work, reports, metadata and cache bytes passed their guards. The operator changed no app source or golden and deleted no data. All local artifacts remain held. These are local Docker workflow/report qualifications, not nf-test assertion reruns or native CI. Default campaign behavior is qualified; custom-option preservation is covered separately by root tests.


This is written by an AI agent (model name unavailable) on Nico DeVeaux’s behalf.
