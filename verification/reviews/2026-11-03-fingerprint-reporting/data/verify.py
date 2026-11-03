#!/usr/bin/env python3
"""Verify packaged bytes and exact scientific values using the standard library."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load(name):
    return json.loads((ROOT / name).read_text())


def expected(name):
    return {sample: {float(x): y for x, y in pairs}
            for sample, pairs in load(name)['expected_plot_curves'].items()}


def check_table(name, curves):
    rows = list(csv.reader((ROOT / name).open(), delimiter='\t'))
    header = rows[0]
    assert header[0] == 'Sample' and len(set(header)) == len(header)
    xs = [float(value) for value in header[1:]]
    assert len(set(xs)) == len(xs)
    assert set(xs) == {x for points in curves.values() for x in points}
    assert len(rows) - 1 == len(curves)
    assert {row[0] for row in rows[1:]} == set(curves)
    cells = 0
    for row in rows[1:]:
        assert len(row) == len(header)
        for x, value in zip(xs, row[1:]):
            if x in curves[row[0]]:
                assert value != '' and float(value) == curves[row[0]][x]
                cells += 1
            else:
                assert value == ''
    assert cells == sum(map(len, curves.values()))
    return cells


def check_plot(name, curves):
    rows = [row for row in csv.reader((ROOT / name).open(), delimiter='\t') if row]
    assert len(rows) == 2 * len(curves)
    actual = {}
    for xs, ys in zip(rows[::2], rows[1::2]):
        assert xs[0] == '' and len(xs) == len(ys) and ys[0] not in actual
        actual[ys[0]] = {float(x): float(y) for x, y in zip(xs[1:], ys[1:])}
        assert len(actual[ys[0]]) == len(xs) - 1
    assert actual == curves


manifest = load('MANIFEST.json')
declared = {row['path'] for row in manifest['files']}
actual = {str(path.relative_to(ROOT)) for path in ROOT.rglob('*') if path.is_file()}
assert actual == declared | {'MANIFEST.json'}, 'Unlisted or missing package file'
for row in manifest['files']:
    path = ROOT / row['path']
    assert not path.is_symlink() and path.resolve().is_relative_to(ROOT)
    data = path.read_bytes()
    assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256']
curves = expected('controls/nf25/EXPECTED.json')
assert curves == expected('controls/nf26/EXPECTED.json')
assert len(curves) == 8 and sum(map(len, curves.values())) == 782
scopes = load('controls/EXPORT-SCOPES.json')['scopes']
for files in scopes.values():
    counts = files['deeptools_plot_fingerprint_counts_mlib_deeptools.txt']
    plot = files['mqc_deeptools_fingerprint_plot_1.txt']
    assert check_table(counts, curves) == 782
    check_plot(plot, curves)
for filename in next(iter(scopes.values())):
    assert len({(ROOT / files[filename]).read_bytes() for files in scopes.values()}) == 1
default = expected('default/EXPECTED.json')
assert len(default) == 6 and sum(map(len, default.values())) == 473
assert check_table('default/repaired/deeptools_plot_fingerprint_counts_mlib_deeptools.txt', default) == 473
check_plot('default/repaired/mqc_deeptools_fingerprint_plot_1.txt', default)
for order in load('legacy/INPUT-BINDINGS.json')['orders']:
    prefix = 'legacy/orders/' + order['name'] + '/'
    row = load(prefix + 'EXPECTED.json')
    legacy = {sample: {float(x): y for x, y in pairs} for sample, pairs in row['parsed_data'].items()}
    assert len(legacy) == 6
    check_plot(prefix + 'mqc_deeptools_fingerprint_plot_1.txt', legacy)
    table = list(csv.reader((ROOT / (prefix + 'deeptools_plot_fingerprint_counts_mlib_deeptools.txt')).open(), delimiter='\t'))
    assert len(table) == 7 and all(not any(row[1:]) for row in table[1:])
print(json.dumps({'manifest_files_verified': len(declared), 'controls_series': 8,
                  'controls_points': 782, 'byte_identical_export_scopes': len(scopes),
                  'default_series': 6, 'default_points': 473,
                  'legacy_orders_verified': 4, 'status': 'PASS'}))
