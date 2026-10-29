#!/usr/bin/env python3
"""Compare nf-core/atacseq consensus featureCounts matrices between pipeline arms.

Why this exists
---------------
The PRs under review change *counting*:
  * #448 (modules update) bumps subread/featureCounts (v2.0.1 -> v2.1.1) and can
    also shift the upstream consensus peak set.
  * #452 (featurecounts mixed SE/PE) changes per-batch endedness handling; its
    effect only appears on a mixed SE/PE cohort.

This tool quantifies those changes directly from the consensus featureCounts
output files, so the answer does not depend on the pre-computed comparison.tsv.

Design notes (correctness)
--------------------------
  * Rows are keyed by GENOMIC COORDINATE (Chr, Start, End), NOT by the Geneid
    (Interval_N). When two arms disagree on the number of consensus peaks, the
    Interval_N numbering diverges after the first insertion, so Geneid joins are
    wrong.
  * Sample columns are matched BY NAME, not position. featureCounts receives BAMs
    in whatever order the Nextflow channel emits, which is not stable across runs.

Re-run for #448 / #452 / dev (or the original paper counts) by pointing the
manifest at the relevant featureCounts files -- no code changes needed:

    python3 compare_featurecounts.py \
        --manifest verification/counts/manifest.tsv \
        --baseline dev \
        --outdir verification/counts

manifest.tsv is two columns (label<TAB>path), one arm per line.

Dependencies: Python 3.8+ standard library only.
"""

import argparse
import math
import os
import sys


def parse_featurecounts(path):
    """Return (version, samples, rows).

    version : featureCounts version string parsed from the '# Program:' comment.
    samples : list of normalized sample names (column order as in the file).
    rows    : dict keyed by (chrom, start, end) -> {sample: int_count}.
    """
    version = "unknown"
    samples = None
    rows = {}
    with open(path) as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.startswith("#"):
                # e.g. "# Program:featureCounts v2.1.1; Command:..."
                marker = "featureCounts "
                if marker in line:
                    tail = line.split(marker, 1)[1]
                    version = tail.split(";", 1)[0].strip()
                continue
            fields = line.split("\t")
            if samples is None:
                # Header row: Geneid Chr Start End Strand Length <sample columns>
                samples = [normalize_sample(s) for s in fields[6:]]
                continue
            if len(fields) < 7:
                continue
            chrom, start, end = fields[1], fields[2], fields[3]
            key = (chrom, start, end)
            counts = {}
            for name, value in zip(samples, fields[6:]):
                counts[name] = int(value)
            rows[key] = counts
    if samples is None:
        raise ValueError(f"No header/data found in {path}")
    return version, samples, rows


def normalize_sample(name):
    for suffix in (".mLb.clN.sorted.bam", ".mRp.clN.sorted.bam", ".sorted.bam", ".bam"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def pearson(xs, ys):
    n = len(xs)
    if n == 0:
        return float("nan")
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx == 0 or dy == 0:
        return float("nan")
    return num / (dx * dy)


def compare(baseline, other):
    """Compare two parsed arms. baseline/other are (label, version, samples, rows)."""
    b_label, b_ver, b_samples, b_rows = baseline
    o_label, o_ver, o_samples, o_rows = other

    b_keys = set(b_rows)
    o_keys = set(o_rows)
    shared = b_keys & o_keys
    only_b = b_keys - o_keys
    only_o = o_keys - b_keys

    shared_samples = [s for s in b_samples if s in set(o_samples)]

    per_sample = []
    for s in shared_samples:
        b_total = sum(b_rows[k][s] for k in b_keys)
        o_total = sum(o_rows[k][s] for k in o_keys)
        deltas = [o_rows[k][s] - b_rows[k][s] for k in shared]
        changed = sum(1 for d in deltas if d != 0)
        sum_abs = sum(abs(d) for d in deltas)
        max_abs = max((abs(d) for d in deltas), default=0)
        r = pearson(
            [b_rows[k][s] for k in shared],
            [o_rows[k][s] for k in shared],
        )
        per_sample.append({
            "sample": s,
            "baseline_total": b_total,
            "other_total": o_total,
            "total_delta": o_total - b_total,
            "changed_intervals": changed,
            "sum_abs_delta": sum_abs,
            "max_abs_delta": max_abs,
            "pearson_r": r,
        })

    return {
        "baseline": b_label,
        "other": o_label,
        "baseline_version": b_ver,
        "other_version": o_ver,
        "baseline_intervals": len(b_keys),
        "other_intervals": len(o_keys),
        "shared_intervals": len(shared),
        "only_baseline": len(only_b),
        "only_other": len(only_o),
        "shared_samples": shared_samples,
        "baseline_only_samples": [s for s in b_samples if s not in set(o_samples)],
        "other_only_samples": [s for s in o_samples if s not in set(b_samples)],
        "per_sample": per_sample,
    }


def fmt_r(r):
    return "NA" if (r != r) else f"{r:.6f}"


def render_markdown(result):
    L = []
    b, o = result["baseline"], result["other"]
    L.append(f"# featureCounts count-change report: `{b}` (baseline) vs `{o}`")
    L.append("")
    L.append("## Consensus peak set (intervals)")
    L.append("")
    L.append("| Metric | Value |")
    L.append("|--------|-------|")
    L.append(f"| featureCounts version ({b}) | `{result['baseline_version']}` |")
    L.append(f"| featureCounts version ({o}) | `{result['other_version']}` |")
    L.append(f"| Intervals in {b} | {result['baseline_intervals']:,} |")
    L.append(f"| Intervals in {o} | {result['other_intervals']:,} |")
    L.append(f"| Shared intervals (by coord) | {result['shared_intervals']:,} |")
    L.append(f"| Intervals only in {b} | {result['only_baseline']:,} |")
    L.append(f"| Intervals only in {o} | {result['only_other']:,} |")
    L.append("")
    L.append("## Per-sample read counts (over shared intervals)")
    L.append("")
    L.append(f"`total_delta` = {o} total - {b} total. `changed_intervals` counts shared "
             f"intervals whose count differs. `pearson_r` is over shared intervals.")
    L.append("")
    L.append("| Sample | " + f"{b} total | {o} total | total delta | changed intervals | sum abs delta | max abs delta | Pearson r |")
    L.append("|--------|-----------:|-----------:|--------:|------------------:|-----:|-------:|----------:|")
    for ps in result["per_sample"]:
        L.append(
            f"| {ps['sample']} | {ps['baseline_total']:,} | {ps['other_total']:,} | "
            f"{ps['total_delta']:+,} | {ps['changed_intervals']:,} | {ps['sum_abs_delta']:,} | "
            f"{ps['max_abs_delta']:,} | {fmt_r(ps['pearson_r'])} |"
        )
    L.append("")
    if result["baseline_only_samples"] or result["other_only_samples"]:
        L.append(f"> Unmatched sample columns -- only in {b}: "
                 f"{result['baseline_only_samples'] or 'none'}; only in {o}: "
                 f"{result['other_only_samples'] or 'none'}")
        L.append("")
    return "\n".join(L)


def render_tsv(result):
    L = ["sample\tbaseline_total\tother_total\ttotal_delta\tchanged_intervals\tsum_abs_delta\tmax_abs_delta\tpearson_r"]
    for ps in result["per_sample"]:
        L.append("\t".join(str(x) for x in [
            ps["sample"], ps["baseline_total"], ps["other_total"], ps["total_delta"],
            ps["changed_intervals"], ps["sum_abs_delta"], ps["max_abs_delta"], fmt_r(ps["pearson_r"]),
        ]))
    return "\n".join(L)


def load_manifest(path):
    inputs = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            label, fpath = line.split("\t")[:2]
            inputs.append((label, fpath))
    return inputs


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", help="TSV of label<TAB>path (one arm per line)")
    ap.add_argument("--input", action="append", default=[], metavar="LABEL=PATH",
                    help="Arm as LABEL=PATH (repeatable). Overrides/extends --manifest.")
    ap.add_argument("--baseline", help="Label to use as baseline (default: first input)")
    ap.add_argument("--outdir", default=".", help="Directory for report outputs")
    args = ap.parse_args(argv)

    inputs = []
    if args.manifest:
        inputs.extend(load_manifest(args.manifest))
    for item in args.input:
        label, fpath = item.split("=", 1)
        inputs.append((label, fpath))

    if len(inputs) < 2:
        ap.error("need at least two arms (via --manifest and/or --input)")

    parsed = {}
    for label, fpath in inputs:
        if not os.path.exists(fpath):
            print(f"WARNING: skipping missing arm '{label}' -> {fpath}", file=sys.stderr)
            continue
        ver, samples, rows = parse_featurecounts(fpath)
        parsed[label] = (label, ver, samples, rows)
        print(f"loaded {label}: {len(rows):,} intervals, {len(samples)} samples, featureCounts {ver}",
              file=sys.stderr)

    if len(parsed) < 2:
        print("ERROR: fewer than two arms available after loading; nothing to compare.", file=sys.stderr)
        return 1

    labels = list(parsed)
    baseline_label = args.baseline or labels[0]
    if baseline_label not in parsed:
        ap.error(f"baseline '{baseline_label}' not among loaded arms {labels}")

    os.makedirs(args.outdir, exist_ok=True)
    md_all = []
    for label in labels:
        if label == baseline_label:
            continue
        result = compare(parsed[baseline_label], parsed[label])
        md_all.append(render_markdown(result))
        tsv_path = os.path.join(args.outdir, f"count_changes.{baseline_label}_vs_{label}.tsv")
        with open(tsv_path, "w") as fh:
            fh.write(render_tsv(result) + "\n")
        print(f"wrote {tsv_path}", file=sys.stderr)

    md_path = os.path.join(args.outdir, "COUNT_CHANGES.md")
    with open(md_path, "w") as fh:
        fh.write("\n\n---\n\n".join(md_all) + "\n")
    print(f"wrote {md_path}", file=sys.stderr)
    print("\n\n".join(md_all))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
