"""Corpus-level check of three songwriting entries together:
 - ideas: two-pass lettering (resolved rhymes claim uppercase letters first, assonance gets lowercase)
 - ideas: Pattison scheme shape -> emotional motion (AABB/ABAB stable, XXAA/ABBA open)
 - local__sandbox-one-stray-merge-flips-open-verdicts/E1 (one stray merge flips open/stable, 7 of 19 collapses)
Every 4-line stanza over a toy phonetic tail inventory is lettered three ways and the
open/stable verdict compared with the resolved-only truth. Deterministic, stdlib only.
"""
from itertools import product
from collections import Counter

MANNER = {'t': 'stop', 'p': 'stop', 'k': 'stop', 's': 'fric', 'f': 'fric', 'n': 'nas', 'm': 'nas'}

def resolved(a, b):  # perfect or family: same vowel, same coda manner
    return a[0] == b[0] and MANNER[a[1]] == MANNER[b[1]]

def assonant(a, b):
    return a[0] == b[0]

def group_first_match(lines, idxs, rel):
    gid = {}
    seen = []
    for i in idxs:
        gid[i] = i
        for j in seen:
            if rel(lines[i], lines[j]):
                gid[i] = gid[j]
                break
        seen.append(i)
    groups = Counter(gid.values())
    return {i: g for i, g in gid.items() if groups[g] >= 2}

def one_pass(lines):
    g = group_first_match(lines, range(4), assonant)
    return [('U', g[i]) if i in g else None for i in range(4)]

def two_pass(lines):
    g1 = group_first_match(lines, range(4), resolved)
    rest = [i for i in range(4) if i not in g1]
    g2 = group_first_match(lines, rest, assonant)
    out = []
    for i in range(4):
        if i in g1: out.append(('U', g1[i]))
        elif i in g2: out.append(('L', g2[i]))
        else: out.append(None)
    return out

def shape(lab, keep_lower):
    names, s = {}, ''
    for x in lab:
        if x is None or (x[0] == 'L' and not keep_lower):
            s += 'X'
        else:
            key = x[1]
            if key not in names:
                names[key] = 'ABCD'[len(names)]
            s += names[key]
    return s

def verdict(sh):
    """companion E1 rule: open if max closure distance >= 3 or nothing closes before the last line."""
    last, gaps, closes = {}, [], []
    for i, c in enumerate(sh):
        if c == 'X':
            continue
        if c in last:
            gaps.append(i - last[c]); closes.append(i)
        last[c] = i
    if not gaps:
        return 'open'
    return 'open' if (max(gaps) >= 3 or min(closes) == 3) else 'stable'

PATTISON = {'AABB': 'stable', 'ABAB': 'stable', 'XXAA': 'open', 'ABBA': 'open'}

def run(vowels, codas, label):
    tails = [(v, c) for v in vowels for c in codas]
    n = 0
    stats = Counter()
    pairs = Counter()
    for st in product(tails, repeat=4):
        n += 1
        truth = shape(two_pass(st), keep_lower=False)
        one = shape(one_pass(st), keep_lower=True)
        tpb = shape(two_pass(st), keep_lower=True)   # two-pass read case-blind
        tv, ov, bv = verdict(truth), verdict(one), verdict(tpb)
        stats['shape_one'] += one != truth
        stats['shape_blind'] += tpb != truth
        if ov != tv:
            stats['flip_one'] += 1
            stats['one_' + tv + '_to_' + ov] += 1
            pairs[(truth, one)] += 1
        if bv != tv:
            stats['flip_blind'] += 1
            stats['blind_' + tv + '_to_' + bv] += 1
        if truth in PATTISON:
            stats['pat_' + truth] += 1
            if ov != PATTISON[truth]:
                stats['pat_flip_one'] += 1
            if bv != PATTISON[truth]:
                stats['pat_flip_blind'] += 1
    print(f"[{label}] tails={len(tails)} stanzas={n}")
    print(f"  one-pass shape wrong {stats['shape_one']} ({100*stats['shape_one']/n:.1f}%), verdict flipped {stats['flip_one']} ({100*stats['flip_one']/n:.1f}%)")
    print(f"    open->stable {stats['one_open_to_stable']}  stable->open {stats['one_stable_to_open']}")
    print(f"  two-pass case-blind shape wrong {stats['shape_blind']}, verdict flipped {stats['flip_blind']} ({100*stats['flip_blind']/n:.1f}%)")
    print(f"    open->stable {stats['blind_open_to_stable']}  stable->open {stats['blind_stable_to_open']}")
    pat_n = sum(stats['pat_' + k] for k in PATTISON)
    print(f"  Pattison-shape stanzas {pat_n} ({', '.join(k+'='+str(stats['pat_'+k]) for k in PATTISON)}); one-pass flips {stats['pat_flip_one']}, case-blind flips {stats['pat_flip_blind']}")
    top = [(f"{a}->{b}", c) for (a, b), c in pairs.most_common(6)]
    print("  top one-pass verdict flips:", top)
    print("  XAAX->ABBA count (one-pass):", pairs[('XAAX', 'ABBA')])
    return stats, n, pairs

# Scenario 1: 3 vowels x 6 codas
s1, n1, p1 = run('iao', 'tpsfnm', 'S1 3 vowels')
# Scenario 2: 5 vowels x 4 codas (more vowels -> fewer stray same-vowel collisions)
s2, n2, p2 = run('ieaou', 'tsnm', 'S2 5 vowels')
# Scenario 3 (built to BREAK "stray assonance only ever closes a stanza"): fixed XAAX stanza
st = [('a', 't'), ('o', 'n'), ('o', 'm'), ('a', 's')]   # bat / bone / foam / class: a-t vs a-s assonance only
tr = shape(two_pass(st), False); on = shape(one_pass(st), True); bl = shape(two_pass(st), True)
print(f"[S3] fixed stanza truth {tr} ({verdict(tr)}), one-pass {on} ({verdict(on)}), two-pass case-blind {bl} ({verdict(bl)})")
s3_break = verdict(tr) == 'stable' and verdict(on) == 'open' and verdict(bl) == 'open'

ok = (s1['one_stable_to_open'] > 0 and s1['one_open_to_stable'] > s1['one_stable_to_open']
      and s1['flip_blind'] < s1['flip_one'] and s1['blind_stable_to_open'] > 0 and s3_break
      and s2['flip_one'] / n2 < s1['flip_one'] / n1)
print(f"RESULT: {'PASS' if ok else 'FAIL'} S1 one-pass flips {s1['flip_one']}/{n1} ({100*s1['flip_one']/n1:.1f}%: {s1['one_open_to_stable']} open->stable, {s1['one_stable_to_open']} stable->open); "
      f"case-blind two-pass flips {s1['flip_blind']} ({s1['blind_stable_to_open']} stable->open); S2 5-vowel one-pass {100*s2['flip_one']/n2:.1f}%; XAAX->ABBA fixed case flips stable->open={s3_break}")
