"""Sandbox: how much does the OPEN tension "is a cluster-coda rhyme (ask/back, last/that)
resolved or open?" matter for the rhyme-scheme SHAPE verdict?

Pipeline (companion lesson's stages: judge -> scope -> pass order, here scope = one
4-line stanza):
  judge   phonetic (vowel, coda) pairs: perfect (same vowel+coda), cluster (same vowel,
          codas differ only by an extra consonant in a cluster, e.g. S K vs K), assonance
          (same vowel only). Policy R counts cluster as resolved, policy O as open.
  letters two-pass: UPPERCASE for resolved pairs first, then lowercase assonance among the
          still-unlettered lines (the two-pass kernel).
  shape   only UPPERCASE letters close a line. Verdict OPEN if the longest closure span
          (line minus its latest same-letter line) >= 3, or the first closing line is line
          4, or nothing closes; else STABLE (the two-metric rule from the shape lessons).
Part A enumerates every 4-line partition with each rhyming block typed perfect / cluster /
assonance. Part B runs real-word stanzas through a hand-written phoneme fixture.
Deterministic, stdlib only.
"""
import itertools

# ---------- verdict on letters ----------

def verdict(letters):
    last, spans, first_close = {}, [], None
    for i, c in enumerate(letters):
        if c.isupper():
            if c in last:
                spans.append(i - last[c])
                if first_close is None:
                    first_close = i + 1
            last[c] = i
    if not spans:
        return 'OPEN'
    return 'OPEN' if max(spans) >= 3 or first_close >= 4 else 'STABLE'

# ---------- two-pass lettering from a pair-type oracle ----------

def two_pass(n, ptype, policy):
    resolved = {'perfect'} | ({'cluster'} if policy == 'R' else set())
    lab = [None] * n
    nxt = 0
    for i in range(n):  # pass 1: resolved only
        if lab[i] is not None:
            continue
        mates = [j for j in range(i + 1, n) if lab[j] is None and ptype(i, j) in resolved]
        if mates:
            L = chr(65 + nxt); nxt += 1
            lab[i] = L
            for j in mates:
                lab[j] = L
    for i in range(n):  # pass 2: assonance (any same-vowel type) among unlettered
        if lab[i] is not None:
            continue
        mates = [j for j in range(i + 1, n) if lab[j] is None and ptype(i, j) is not None]
        L = chr(97 + nxt); nxt += 1
        lab[i] = L
        for j in mates:
            lab[j] = L
    # unrhymed singles: mark 'x'
    out = []
    for i, c in enumerate(lab):
        out.append(c if sum(1 for d in lab if d == c) > 1 else 'x')
    return ''.join(out)


def partitions(items):
    if not items:
        yield []
        return
    first, rest = items[0], items[1:]
    for p in partitions(rest):
        yield [[first]] + p
        for k in range(len(p)):
            yield p[:k] + [[first] + p[k]] + p[k + 1:]


def part_a():
    total, with_cluster, flips, r_open_o_stable, o_open_r_stable = 0, 0, 0, 0, 0
    named = {}
    for part in partitions([0, 1, 2, 3]):
        blocks = [b for b in part if len(b) >= 2]
        for types in itertools.product(['perfect', 'cluster', 'assonance'], repeat=len(blocks)):
            total += 1
            bt = {}
            for b, t in zip(blocks, types):
                for i in b:
                    bt[i] = (tuple(b), t)

            def ptype(i, j):
                if i in bt and j in bt and bt[i][0] == bt[j][0]:
                    return bt[i][1]
                return None
            vR = verdict(two_pass(4, ptype, 'R'))
            vO = verdict(two_pass(4, ptype, 'O'))
            if 'cluster' in types:
                with_cluster += 1
                if vR != vO:
                    flips += 1
                    if vR == 'OPEN':
                        r_open_o_stable += 1
                    else:
                        o_open_r_stable += 1
            # named shapes with exactly one cluster block, others perfect
            shape = ''.join('ABCD'[next(k for k, b in enumerate(sorted(blocks)) if i in b)] if i in bt else 'X' for i in range(4))
            if types.count('cluster') == 1 and all(t in ('perfect', 'cluster') for t in types):
                key = None
                canon = {'AABB': 'AABB', 'ABAB': 'ABAB', 'ABBA': 'ABBA', 'XXAA': 'XXAA'}
                # canonical letters by first appearance
                m, s = {}, ''
                for ch in shape:
                    if ch == 'X':
                        s += 'X'
                    else:
                        m.setdefault(ch, 'AB'[len(m)] if len(m) < 2 else 'C')
                        s += m[ch]
                if s in canon:
                    cl = [b for b, t in zip(blocks, types) if t == 'cluster'][0]
                    named[(s, tuple(cl))] = (vR, vO)
    return total, with_cluster, flips, r_open_o_stable, o_open_r_stable, named

# ---------- Part B: real words with a hand phoneme fixture ----------

PH = {'ask': ('AE', 'SK'), 'back': ('AE', 'K'), 'task': ('AE', 'SK'), 'black': ('AE', 'K'),
      'last': ('AE', 'ST'), 'that': ('AE', 'T'), 'past': ('AE', 'ST'), 'cat': ('AE', 'T'),
      'mist': ('IH', 'ST'), 'kiss': ('IH', 'S'), 'list': ('IH', 'ST'), 'this': ('IH', 'S'),
      'rain': ('EY', 'N'), 'again': ('EY', 'N'), 'stone': ('OW', 'N'), 'home': ('OW', 'M'),
      'night': ('AY', 'T'), 'light': ('AY', 'T'), 'fire': ('AY', 'ER'), 'tide': ('AY', 'D')}


def word_ptype(a, b):
    va, ca = PH[a]; vb, cb = PH[b]
    if va != vb:
        return None
    if ca == cb:
        return 'perfect'
    long_, short = (ca, cb) if len(ca) > len(cb) else (cb, ca)
    if short and len(long_) - len(short) == 1 and (long_.startswith(short) or long_.endswith(short)):
        return 'cluster'
    return 'assonance'

STANZAS = [
    ('ABBA outer cluster', ['ask', 'rain', 'again', 'back']),
    ('ABBA inner cluster', ['rain', 'mist', 'kiss', 'again']),
    ('ABAB first-pair cluster', ['last', 'night', 'that', 'light']),
    ('ABAB second-pair cluster', ['night', 'last', 'light', 'that']),
    ('AABB cluster couplet', ['ask', 'back', 'night', 'light']),
    ('XXAA cluster close', ['stone', 'fire', 'list', 'this']),
    ('control: no cluster ABBA', ['rain', 'night', 'light', 'again']),
]


def part_b():
    rows = []
    for name, words in STANZAS:
        pt = lambda i, j: word_ptype(words[i], words[j])
        lR, lO = two_pass(4, pt, 'R'), two_pass(4, pt, 'O')
        rows.append((name, words, lR, verdict(lR), lO, verdict(lO)))
    return rows


if __name__ == '__main__':
    total, wc, flips, ro, orr, named = part_a()
    print(f'Part A: {total} typed 4-line configurations, {wc} contain a cluster block')
    print(f'   verdict flips between policies: {flips}/{wc} ({100*flips/wc:.1f}%); '
          f'cluster-resolved OPEN but cluster-open STABLE: {ro}; reverse: {orr}')
    nflip = 0
    for (s, cl), (vR, vO) in sorted(named.items()):
        nflip += vR != vO
        print(f'   {s} cluster on lines {[c+1 for c in cl]}: R {vR:6s} O {vO:6s} {"FLIP" if vR != vO else ""}')
    print('Part B: real words')
    bflip = 0
    for name, w, lR, vR, lO, vO in part_b():
        bflip += vR != vO
        print(f'   {name:26s} {"/".join(w):24s} R {lR} {vR:6s} O {lO} {vO:6s} {"FLIP" if vR != vO else ""}')
    ok = nflip == 2 and 0.20 <= flips / wc <= 0.60
    print(f"RESULT: {'PASS' if ok else 'FAIL'} cluster-coda policy flips the shape verdict in {flips}/{wc} typed configurations "
          f"({ro} toward open when cluster counts as resolved, {orr} the other way); named shapes with one cluster pair flip "
          f"{nflip}/{len(named)}; real-word stanzas flip {bflip}/{len(STANZAS)}")
