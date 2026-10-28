from pathlib import Path
import gzip
import json

root = Path(__file__).parent
observed = {}
for label in ('poly-nf-base', 'poly-nf-current', 'poly-nf-disabled'):
    mates = {}
    for mate in (1, 2):
        path = root / label / 'outputs' / f'poly_{mate}_val_{mate}.fq.gz'
        with gzip.open(path, 'rt') as stream:
            sequences = [line.strip() for index, line in enumerate(stream) if index % 4 == 1]
        assert len(sequences) == 100, (label, mate, len(sequences))
        assert len(set(sequences)) == 1, (label, mate)
        mates[str(mate)] = sequences[0]
    observed[label] = mates
assert observed['poly-nf-base'] == observed['poly-nf-disabled'], observed
for mate in ('1', '2'):
    before = observed['poly-nf-base'][mate]
    after = observed['poly-nf-current'][mate]
    assert len(before) - len(after) == 20, (mate, before, after)
assert observed['poly-nf-base']['2'].startswith('C' * 20)
assert observed['poly-nf-current']['2'] == observed['poly-nf-base']['2'][20:]
(root / 'poly-comparison.json').write_text(json.dumps(observed, indent=2) + '\n')
print('CONFIRMED: actual base module and 0.6.10 preserve R2 20-C heads; current module and 2.1.0 silently remove 20 bases from R2 5-prime ends; --no_poly_g restores exact base sequences. All 100 pairs survive in all three runs.')
