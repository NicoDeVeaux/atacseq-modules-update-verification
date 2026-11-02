# Original ataqv viewer resources

This additive archive preserves all 26 originally published ataqv HTML-tree files from each of the four historical HIV workflow cases: 104 files, 16,757,768 expanded bytes. It includes their original index pages, CSS, JavaScript, fonts, configuration and per-library compressed JSON data. The four index payloads are byte-identical to those in the earlier report-object supplement. Fixed cases used a9b588; unfixed cases used 73155d. Exact source commits, workflow IDs and original/distributed content identities are in `ataqv-viewer-manifest.json`.

This is a subset of the four output trees, separate from the unfinished complete output archive. It adds the originally published companion assets without changing the scientific outputs or inventing replacements. No browser, artifact JavaScript or scientific workflow was executed for this packaging.

Download the five uniquely named files from the [report-object supplement release](https://github.com/NicoDeVeaux/atacseq-modules-update-verification/releases/tag/pr448-hiv-report-objects-2026-11-02): `ataqv-viewer-resources.tar.gz`, `ataqv-viewer-manifest.json`, `verify-ataqv.py`, `ATAQV-LICENSE.txt` and this document. Additive assets become available when uploaded.

```sh
python3 -B verify-ataqv.py
python3 -B verify-ataqv.py --self-test
```

The standard-library verifier hashes the complete gzip file, streams every normalized regular TAR member and checks the exact inventory, sizes and member hashes. It also verifies the separate license document's size and hash. It neither extracts nor executes resources. Pass `--manifest-sha256 FULL_SHA256` when a trusted parent manifest hash is available. Integrity does not establish manifest authenticity or scientific correctness.

After verification, extract into a new empty directory:

```sh
mkdir ataqv-unpacked
tar -xzf ataqv-viewer-resources.tar.gz -C ataqv-unpacked
```

Resources retain `files/CASE/ALIGNER/merged_library/ataqv/broad_peak/html/` paths. Preserve each complete directory when inspecting a report.

The original published trees contain inherited missing requests: `index.html` references `js/datatables.buttons.min.js`, and DataTables CSS references five absent sorting PNGs under `DataTables-1.10.12/images/`. The combined `datatables.min.js` header already lists Buttons1.2.2, and its code contains `DataTable.Buttons`, supporting that the extra standalone Buttons script request is redundant. All declared configuration data and font references are present. These observations are static; browser behavior was not tested. The original index/CSS bytes remain unchanged.

Original third-party copyright and license notices remain in the assets. In particular, ataqv JavaScript retains its GPLv3-or-later notice; Font Awesome distinguishes font SIL OFL1.1 from CSS MIT; bundled DataTables, jQuery, normalize.css, D3, JSZip and pako notices remain intact. The pipeline's MIT license does not relicense these viewer assets. No binaries or container images are added.

`ATAQV-LICENSE.txt` is the complete GPLv3 text copied from [GNU's official source](https://www.gnu.org/licenses/gpl-3.0.txt). Its URL, byte size and hash are recorded in the manifest. The license document is outside the unchanged 104-member resource archive.

This is written by an AI agent (model name unavailable) on Nico DeVeaux's behalf.
