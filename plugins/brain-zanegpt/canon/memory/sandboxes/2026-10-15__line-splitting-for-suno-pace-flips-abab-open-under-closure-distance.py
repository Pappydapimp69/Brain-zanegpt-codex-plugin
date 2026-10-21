"""Pass 5 sandbox: rhyme-scheme shape kernel x hyphenate/shorter-lines kernel x
closure-distance two-metric rule (local__sandbox-closure-distance-calls-xxaa-closed E1).
Deterministic, stdlib only.
Rule: a stanza is OPEN if its max closure distance >= 3 or nothing closes before the
last line; otherwise STABLE. Kernel verdicts: AABB stable, ABAB stable, ABBA open, XXAA open.
Closure distance of a rhyme group = gap between consecutive members (in lines).
Shorter-lines fix: split a rushed line after its midpoint word; the new first half ends on
a mid-line word (unrhymed 'x' unless the fixture gives it an internal rhyme letter).
"""
KERNEL = {'AABB': 'stable', 'ABAB': 'stable', 'ABBA': 'open', 'XXAA': 'open'}

def verdict(letters, pos=None):
    """letters: list of rhyme letters per line ('x'/'X' = unrhymed); pos: line index per item."""
    pos = pos if pos is not None else list(range(1, len(letters) + 1))
    last = pos[-1]
    groups = {}
    for l, p in zip(letters, pos):
        if l.lower() == 'x':
            continue
        groups.setdefault(l, []).append(p)
    dists, first_close = [], None
    for ps in groups.values():
        for a, b in zip(ps, ps[1:]):
            dists.append(b - a)
            first_close = b if first_close is None else min(first_close, b)
    mx = max(dists) if dists else 0
    is_open = mx >= 3 or first_close is None or first_close >= last
    return ('open' if is_open else 'stable'), mx, first_close

# fixture: scheme -> list of stanzas; each line = (word count, end letter, mid-word letter)
STANZAS = [
    ('AABB', [(11, 'A', 'x'), (10, 'A', 'x'), (11, 'B', 'x'), (9, 'B', 'x')]),
    ('AABB', [(11, 'A', 'x'), (6, 'A', 'x'), (10, 'B', 'x'), (5, 'B', 'x')]),
    ('ABAB', [(10, 'A', 'x'), (11, 'B', 'x'), (10, 'A', 'x'), (12, 'B', 'x')]),
    ('ABAB', [(10, 'A', 'x'), (5, 'B', 'x'), (11, 'A', 'x'), (6, 'B', 'x')]),
    ('ABBA', [(11, 'A', 'x'), (10, 'B', 'x'), (9, 'B', 'x'), (11, 'A', 'x')]),
    ('ABBA', [(6, 'A', 'x'), (11, 'B', 'x'), (10, 'B', 'x'), (5, 'A', 'x')]),
    ('XXAA', [(11, 'X', 'x'), (10, 'X', 'x'), (11, 'A', 'x'), (10, 'A', 'x')]),
    ('XXAA', [(5, 'X', 'x'), (11, 'X', 'x'), (6, 'A', 'x'), (11, 'A', 'x')]),
]
BREAK = ('XXAA', [(11, 'X', 'c'), (10, 'X', 'c'), (11, 'A', 'x'), (10, 'A', 'x')])

def split(stanza, only_long):
    letters, src = [], []
    for i, (wc, end, mid) in enumerate(stanza, start=1):
        if (not only_long) or wc > 8:
            letters += [mid, end]; src += [i, i]
        else:
            letters.append(end); src.append(i)
    return letters, src

def run(stanza, mode):
    base = [end for _, end, _ in stanza]
    if mode in ('original', 'hyphenate'):  # hyphenation re-times syllables, lines unchanged
        return verdict(base)
    only_long = mode.startswith('partial')
    letters, src = split(stanza, only_long)
    if mode.endswith('raw'):
        return verdict(letters)
    if mode.endswith('fixA'):  # divide distances by the nominal split factor 2
        pos = [p / 2 for p in range(1, len(letters) + 1)]
        return verdict(letters, pos)
    if mode.endswith('fixC'):  # score only original line-end words at source-line indices
        keep = [(l, s) for k, (l, s) in enumerate(zip(letters, src)) if k + 1 == len(src) or src[k + 1] != s]
        return verdict([l for l, _ in keep], [s for _, s in keep])

MODES = ['original', 'hyphenate', 'all-raw', 'all-fixA', 'all-fixC', 'partial-raw', 'partial-fixA', 'partial-fixC']

def main():
    flips = {m: [] for m in MODES}
    for idx, (scheme, st) in enumerate(STANZAS):
        row = []
        for m in MODES:
            v, mx, fc = run(st, m)
            if v != KERNEL[scheme]:
                flips[m].append(f'{scheme}#{idx}')
            row.append(f'{m}:{v[0].upper()}(d{mx:g},c{fc if fc is None else round(fc, 1)})')
        print(f'{scheme} #{idx}: ' + ' '.join(row))
    for m in MODES:
        print(f'{m:13s} wrong verdicts {len(flips[m])}/8 {flips[m]}')
    b = {m: run(BREAK[1], m)[0] for m in ('original', 'all-raw', 'all-fixC')}
    print('BREAK XXAA with rhyming mid-line words:', b)
    ok = (len(flips['original']) == 0 and len(flips['hyphenate']) == 0
          and sorted(set(s.split('#')[0] for s in flips['all-raw'])) == ['ABAB'] and len(flips['all-raw']) == 2
          and len(flips['partial-raw']) >= 1 and len(flips['all-fixA']) == 0 and len(flips['partial-fixA']) >= 1
          and len(flips['all-fixC']) == 0 and len(flips['partial-fixC']) == 0
          and b['all-raw'] == 'stable' and b['all-fixC'] == 'open')
    print(f"RESULT: {'PASS' if ok else 'FAIL'} wrong verdicts out of 8: hyphenate {len(flips['hyphenate'])}, split-all raw "
          f"{len(flips['all-raw'])} {flips['all-raw']}, partial split raw {len(flips['partial-raw'])} {flips['partial-raw']}, "
          f"halve-distances fix {len(flips['all-fixA'])} all / {len(flips['partial-fixA'])} partial, source-line-end fix "
          f"{len(flips['all-fixC'])}/{len(flips['partial-fixC'])}; break XXAA raw {b['all-raw']} vs fixC {b['all-fixC']}")

if __name__ == '__main__':
    main()
