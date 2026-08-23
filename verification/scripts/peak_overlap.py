#!/usr/bin/env python3
"""Compute and visualize genomic peak-set overlap across arbitrary N peak sets.

Purpose
-------
Compare ATAC-seq consensus peak sets that live on the *same genome build* --
here the original paper's GRCh38 peak set (GSE125918 Table S3, 87,681 peaks)
against nf-core/atacseq consensus peaks from `dev`, the modules-update `branch`,
and (when available) PR #448 / #452 runs.

No third-party deps: pure Python stdlib. No bedtools, no matplotlib. Overlap is
computed with a per-chromosome sweep; the figure is emitted as hand-written SVG.

Method (correct set partitioning for N sets)
-------------------------------------------
A naive "peaks of A overlapping B" count is asymmetric and cannot be assembled
into a clean Venn/UpSet. Instead we build a shared universe:

  1. Concatenate intervals from ALL sets and MERGE overlapping ones per chrom
     into disjoint "union regions" (like a bedtools multiinter/merge universe).
  2. For each union region, membership = the set of input labels that have at
     least one peak overlapping that region.
  3. Count union regions per membership-combination. These counts partition the
     universe exactly, so they drop straight into an UpSet plot (and a Venn for
     N<=3).

We also report, separately, the raw asymmetric reciprocal overlap and a Jaccard
matrix in union-region space, because reviewers ask both "how partitioned is the
universe" and "pairwise, how concordant are two arms".

Re-run for #448 / #452
----------------------
Just add lines to the manifest (label<TAB>bed_path) and re-run; the tool adapts
to any number of sets. BED-like inputs are fine: any line whose 2nd/3rd fields
are not integers (e.g. headers) is skipped.

    python3 peak_overlap.py --manifest verification/overlap/manifest.tsv \
        --outdir verification/overlap --min-overlap 1

Dependencies: Python 3.8+ standard library only.
"""

import argparse
import os
import sys


# ----------------------------- parsing / merging -----------------------------

def read_bed(path):
    """Return {chrom: [(start, end), ...]} from a BED-like file (0/1-based agnostic
    for overlap purposes). Skips headers/comment lines automatically."""
    by_chrom = {}
    with open(path) as fh:
        for line in fh:
            if not line.strip() or line.startswith(("#", "track", "browser")):
                continue
            f = line.rstrip("\n").split("\t")
            if len(f) < 3:
                continue
            chrom, s, e = f[0], f[1], f[2]
            if not (s.isdigit() and e.isdigit()):
                continue  # header row such as "Chromosome Start End"
            s, e = int(s), int(e)
            if e < s:
                s, e = e, s
            by_chrom.setdefault(chrom, []).append((s, e))
    for c in by_chrom:
        by_chrom[c].sort()
    return by_chrom


def merge_intervals(intervals):
    """Merge a sorted list of (start, end) into disjoint intervals."""
    if not intervals:
        return []
    merged = [list(intervals[0])]
    for s, e in intervals[1:]:
        if s <= merged[-1][1]:
            if e > merged[-1][1]:
                merged[-1][1] = e
        else:
            merged.append([s, e])
    return [(s, e) for s, e in merged]


def build_union(sets_by_chrom):
    """sets_by_chrom: {label: {chrom: [(s,e)]}} -> {chrom: [(s,e)] disjoint union}."""
    union = {}
    for label, by_chrom in sets_by_chrom.items():
        for chrom, ivs in by_chrom.items():
            union.setdefault(chrom, []).extend(ivs)
    for chrom in union:
        union[chrom].sort()
        union[chrom] = merge_intervals(union[chrom])
    return union


# ----------------------------- overlap queries -------------------------------

def overlaps_any(query, sorted_ivs, min_overlap):
    """True if `query`=(qs,qe) overlaps any interval in sorted_ivs by >= min_overlap bp.
    sorted_ivs is sorted by start; linear-ish scan with early break."""
    qs, qe = query
    # binary search for first interval whose end could reach qs
    lo, hi = 0, len(sorted_ivs)
    while lo < hi:
        mid = (lo + hi) // 2
        if sorted_ivs[mid][1] < qs:
            lo = mid + 1
        else:
            hi = mid
    for s, e in sorted_ivs[lo:]:
        if s >= qe:
            break
        ov = min(qe, e) - max(qs, s)
        if ov >= min_overlap:
            return True
    return False


def membership_counts(labels, sets_by_chrom, union, min_overlap):
    """For each union region, compute which labels overlap it. Return:
      combo_counts: {frozenset(labels): n_union_regions}
      set_universe_size: {label: n_union_regions that label is a member of}
    """
    combo_counts = {}
    set_universe = {lab: 0 for lab in labels}
    # pre-index each set's intervals sorted by start (already sorted in read_bed)
    for chrom, regions in union.items():
        per_label = {lab: sets_by_chrom.get(lab, {}).get(chrom, []) for lab in labels}
        for region in regions:
            members = frozenset(
                lab for lab in labels
                if per_label[lab] and overlaps_any(region, per_label[lab], min_overlap)
            )
            if not members:
                continue
            combo_counts[members] = combo_counts.get(members, 0) + 1
            for lab in members:
                set_universe[lab] += 1
    return combo_counts, set_universe


def pairwise_jaccard(labels, combo_counts):
    """Jaccard over union regions: |A&B| / |A|B|, computed from combo counts."""
    mat = {}
    for a in labels:
        for b in labels:
            inter = sum(n for combo, n in combo_counts.items() if a in combo and b in combo)
            uni = sum(n for combo, n in combo_counts.items() if a in combo or b in combo)
            mat[(a, b)] = (inter, uni, (inter / uni) if uni else float("nan"))
    return mat


def raw_reciprocal(labels, sets_by_chrom, min_overlap):
    """Asymmetric: for (A,B), count peaks of A overlapping any peak of B."""
    out = {}
    for a in labels:
        for b in labels:
            if a == b:
                continue
            n_a = 0
            hit = 0
            for chrom, ivs in sets_by_chrom.get(a, {}).items():
                bivs = sets_by_chrom.get(b, {}).get(chrom, [])
                for iv in ivs:
                    n_a += 1
                    if bivs and overlaps_any(iv, bivs, min_overlap):
                        hit += 1
            # count peaks on chroms absent from b
            for chrom, ivs in sets_by_chrom.get(a, {}).items():
                if chrom not in sets_by_chrom.get(b, {}):
                    pass  # already counted in n_a; no hits possible
            out[(a, b)] = (hit, n_a, (hit / n_a) if n_a else float("nan"))
    return out


# ----------------------------- SVG (UpSet) -----------------------------------

def render_upset_svg(labels, combo_counts, set_universe, raw_sizes, top=20):
    combos = sorted(combo_counts.items(), key=lambda kv: (-kv[1], -len(kv[0])))
    combos = combos[:top]
    n_combos = len(combos)
    n_sets = len(labels)

    # order sets by universe size desc for the matrix rows
    ordered = sorted(labels, key=lambda l: -set_universe.get(l, 0))

    # layout
    pad = 20
    label_w = 210
    bar_top_h = 240
    col_w = 46
    matrix_row_h = 30
    setbar_h = 22
    matrix_h = n_sets * matrix_row_h
    plot_w = n_combos * col_w
    W = pad + label_w + plot_w + pad + 30
    H = pad + 30 + bar_top_h + 12 + matrix_h + pad + 20
    max_count = max((c for _, c in combos), default=1)
    max_setsize = max((set_universe.get(l, 0) for l in ordered), default=1)

    def x_col(i):
        return pad + label_w + i * col_w + col_w / 2

    matrix_y0 = pad + 30 + bar_top_h + 12
    s = []
    s.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
             f'font-family="Helvetica,Arial,sans-serif" font-size="12">')
    s.append(f'<rect width="{W}" height="{H}" fill="white"/>')
    s.append(f'<text x="{pad}" y="{pad}" font-size="15" font-weight="bold">'
             f'ATAC-seq consensus peak overlap (GRCh38 union regions)</text>')

    # top intersection bars
    for i, (combo, cnt) in enumerate(combos):
        h = (cnt / max_count) * (bar_top_h - 10)
        x = x_col(i) - col_w * 0.32
        y = pad + 30 + (bar_top_h - h)
        s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{col_w*0.64:.1f}" height="{h:.1f}" '
                 f'fill="#3b6ea5"/>')
        s.append(f'<text x="{x_col(i):.1f}" y="{y-3:.1f}" text-anchor="middle" '
                 f'font-size="10">{cnt:,}</text>')

    # matrix dots
    for r, lab in enumerate(ordered):
        cy = matrix_y0 + r * matrix_row_h + matrix_row_h / 2
        # row background stripe
        if r % 2 == 0:
            s.append(f'<rect x="{pad+label_w}" y="{cy-matrix_row_h/2:.1f}" '
                     f'width="{plot_w}" height="{matrix_row_h}" fill="#f2f2f2"/>')
        # left label + universe size bar
        s.append(f'<text x="{pad}" y="{cy+4:.1f}" font-size="12">{lab}</text>')
        bw = (set_universe.get(lab, 0) / max_setsize) * (label_w - 120)
        s.append(f'<rect x="{pad+110}" y="{cy-setbar_h/2:.1f}" width="{bw:.1f}" '
                 f'height="{setbar_h}" fill="#c9a13b" opacity="0.6"/>')
        s.append(f'<text x="{pad+112}" y="{cy+4:.1f}" font-size="9" fill="#333">'
                 f'{set_universe.get(lab,0):,}</text>')
        for i, (combo, _) in enumerate(combos):
            cx = x_col(i)
            on = lab in combo
            color = "#222" if on else "#cccccc"
            s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="6" fill="{color}"/>')
        # connect dots vertically within a combo
    for i, (combo, _) in enumerate(combos):
        rows_on = [r for r, lab in enumerate(ordered) if lab in combo]
        if len(rows_on) > 1:
            cx = x_col(i)
            y1 = matrix_y0 + min(rows_on) * matrix_row_h + matrix_row_h / 2
            y2 = matrix_y0 + max(rows_on) * matrix_row_h + matrix_row_h / 2
            s.append(f'<line x1="{cx:.1f}" y1="{y1:.1f}" x2="{cx:.1f}" y2="{y2:.1f}" '
                     f'stroke="#222" stroke-width="2"/>')

    s.append(f'<text x="{pad}" y="{pad+30+bar_top_h/2:.0f}" font-size="11" '
             f'fill="#666" transform="rotate(-90 {pad-4} {pad+30+bar_top_h/2:.0f})">'
             f'intersection size (union regions)</text>')
    s.append('</svg>')
    return "\n".join(s)


# ----------------------------- reporting -------------------------------------

def combo_str(combo, labels):
    return " & ".join(l for l in labels if l in combo)


def render_markdown(labels, combo_counts, set_universe, raw_sizes, jac, recip, params):
    L = []
    L.append("# ATAC-seq consensus peak overlap")
    L.append("")
    L.append(f"All peak sets are on **GRCh38** (UCSC `chr` naming). Overlap universe is built by "
             f"merging every set's intervals into disjoint **union regions**; a set is a member of "
             f"a region if it has >= {params['min_overlap']} bp overlap. Membership-combination "
             f"counts below partition the universe exactly.")
    L.append("")
    L.append("## Set sizes")
    L.append("")
    L.append("| Set | Raw peaks | Union regions covered |")
    L.append("|-----|----------:|----------------------:|")
    for lab in labels:
        L.append(f"| {lab} | {raw_sizes[lab]:,} | {set_universe.get(lab,0):,} |")
    L.append("")
    L.append("## Intersection breakdown (UpSet)")
    L.append("")
    L.append("| Combination | Union regions |")
    L.append("|-------------|--------------:|")
    for combo, cnt in sorted(combo_counts.items(), key=lambda kv: -kv[1]):
        L.append(f"| {combo_str(combo, labels)} | {cnt:,} |")
    L.append("")
    L.append("## Pairwise Jaccard (union-region space)")
    L.append("")
    L.append("| | " + " | ".join(labels) + " |")
    L.append("|" + "---|" * (len(labels) + 1))
    for a in labels:
        row = [a]
        for b in labels:
            inter, uni, j = jac[(a, b)]
            row.append("1.000" if a == b else (f"{j:.3f}" if j == j else "NA"))
        L.append("| " + " | ".join(row) + " |")
    L.append("")
    L.append("## Raw reciprocal overlap (asymmetric: % of row's peaks overlapping column)")
    L.append("")
    L.append("| row \\ col | " + " | ".join(labels) + " |")
    L.append("|" + "---|" * (len(labels) + 1))
    for a in labels:
        row = [a]
        for b in labels:
            if a == b:
                row.append("-")
            else:
                hit, n, frac = recip[(a, b)]
                row.append(f"{frac*100:.1f}% ({hit:,}/{n:,})" if frac == frac else "NA")
        L.append("| " + " | ".join(row) + " |")
    L.append("")
    return "\n".join(L)


def load_manifest(path):
    items = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            items.append((parts[0], parts[1]))
    return items


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", required=True, help="TSV of label<TAB>bed_path")
    ap.add_argument("--outdir", default=".", help="output directory")
    ap.add_argument("--min-overlap", type=int, default=1, help="min overlap in bp to count (default 1)")
    args = ap.parse_args(argv)

    items = load_manifest(args.manifest)
    labels = []
    sets_by_chrom = {}
    raw_sizes = {}
    for label, path in items:
        if not os.path.exists(path):
            print(f"WARNING: skipping missing set '{label}' -> {path}", file=sys.stderr)
            continue
        by_chrom = read_bed(path)
        sets_by_chrom[label] = by_chrom
        raw_sizes[label] = sum(len(v) for v in by_chrom.values())
        labels.append(label)
        print(f"loaded {label}: {raw_sizes[label]:,} peaks on {len(by_chrom)} chroms", file=sys.stderr)

    if len(labels) < 2:
        print("ERROR: need at least two peak sets.", file=sys.stderr)
        return 1

    union = build_union(sets_by_chrom)
    n_union = sum(len(v) for v in union.values())
    print(f"union universe: {n_union:,} disjoint regions", file=sys.stderr)

    combo_counts, set_universe = membership_counts(labels, sets_by_chrom, union, args.min_overlap)
    jac = pairwise_jaccard(labels, combo_counts)
    recip = raw_reciprocal(labels, sets_by_chrom, args.min_overlap)

    os.makedirs(args.outdir, exist_ok=True)
    params = {"min_overlap": args.min_overlap}

    md = render_markdown(labels, combo_counts, set_universe, raw_sizes, jac, recip, params)
    md_path = os.path.join(args.outdir, "PEAK_OVERLAP.md")
    with open(md_path, "w") as fh:
        fh.write(md + "\n")

    svg = render_upset_svg(labels, combo_counts, set_universe, raw_sizes)
    svg_path = os.path.join(args.outdir, "peak_overlap_upset.svg")
    with open(svg_path, "w") as fh:
        fh.write(svg)

    # machine-readable combo counts
    tsv_path = os.path.join(args.outdir, "peak_overlap_combos.tsv")
    with open(tsv_path, "w") as fh:
        fh.write("combination\tunion_regions\n")
        for combo, cnt in sorted(combo_counts.items(), key=lambda kv: -kv[1]):
            fh.write(f"{combo_str(combo, labels)}\t{cnt}\n")

    print(f"wrote {md_path}\nwrote {svg_path}\nwrote {tsv_path}", file=sys.stderr)
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
