"""Sandbox: sung-timing marks (hyphen splits AND vowel elongations like lo-o-ove,
niiight, seeee) against three rhyme-judge stages:
  S        spelling judge: strip hyphens, compare last two letters (suno-builder style)
  P-rejoin phonetic dictionary judge after only removing hyphens
  P-c1     phonetic judge after collapsing every repeated-letter run to ONE letter
  P-first  try every run at 1 or 2 letters, take the first dictionary hit (1 before 2)
  P-ctx    same candidates, break ties by the candidate that perfect-rhymes another line
  P-flag   same candidates, but a token with 2+ dictionary hits is FLAGGED, not judged
Lettering: two-pass (same letter only for perfect rhyme; assonance never merges).
One row also runs single-pass (perfect OR assonance merges) for the companion contrast.
Truth: two-pass phonetic lettering of the words the writer intended.
Hand-written toy phoneme fixture (vowel, coda) - not CMUdict. Deterministic, stdlib only.
"""
import itertools, re

PH = {  # last stressed vowel + coda
    'love': ('AH', 'V'), 'dove': ('AH', 'V'), 'above': ('AH', 'V'), 'move': ('UW', 'V'),
    'night': ('AY', 'T'), 'light': ('AY', 'T'), 'tonight': ('AY', 'T'), 'bright': ('AY', 'T'),
    'see': ('IY', ''), 'free': ('IY', ''), 'me': ('IY', ''),
    'moon': ('UW', 'N'), 'soon': ('UW', 'N'),
    'feel': ('IY', 'L'), 'real': ('IY', 'L'),
    'mud': ('AH', 'D'), 'blood': ('AH', 'D'), 'truck': ('AH', 'K'),
    'alone': ('OW', 'N'), 'phone': ('OW', 'N'), 'stone': ('OW', 'N'), 'home': ('OW', 'M'),
    'good': ('UH', 'D'), 'stood': ('UH', 'D'), 'god': ('AA', 'D'), 'nod': ('AA', 'D'),
    'shoot': ('UW', 'T'), 'root': ('UW', 'T'), 'shot': ('AA', 'T'), 'hot': ('AA', 'T'),
}

STANZAS = [  # (name, sung tokens as written, intended words)
    ('C1 clean eye-rhyme', ['love', 'move', 'above', 'dove'], ['love', 'move', 'above', 'dove']),
    ('C2 clean mud/blood', ['mud', 'night', 'blood', 'light'], ['mud', 'night', 'blood', 'light']),
    ('C3 clean truck', ['truck', 'mud', 'blood', 'light'], ['truck', 'mud', 'blood', 'light']),
    ('H1 hyphen timing', ['to-night', 'a-lone', 'bright', 'stone'], ['tonight', 'alone', 'bright', 'stone']),
    ('E1 elongated love', ['lo-o-ove', 'niiight', 'above', 'light'], ['love', 'night', 'above', 'light']),
    ('E2 elongated see/moon', ['seeee', 'moo-oon', 'free', 'soon'], ['see', 'moon', 'free', 'soon']),
    ('E3 elongated feel', ['fe-e-el', 'a-lo-o-one', 'real', 'phone'], ['feel', 'alone', 'real', 'phone']),
    ('B1 ambiguous, partners help', ['goood', 'shooot', 'stood', 'root'], ['good', 'shoot', 'stood', 'root']),
    ('B2 ambiguous, partners mislead', ['goood', 'shooot', 'nod', 'hot'], ['good', 'shoot', 'nod', 'hot']),
]


def runs(w):
    return [(k, len(list(g))) for k, g in itertools.groupby(w)]


def candidates(tok):
    w = tok.replace('-', '')
    rs = runs(w)
    opts = [[c * 1] if n == 1 else [c * 1, c * 2] for c, n in rs]
    out = []
    for combo in itertools.product(*opts):
        cand = ''.join(combo)
        if cand in PH and cand not in out:
            out.append(cand)
    return out  # product order puts 1-letter collapses first


def perfect(a, b):
    return a is not None and b is not None and a == b


def assonant(a, b):
    return a is not None and b is not None and a[0] == b[0]


def letters(keys, single_pass=False, judge=perfect):
    groups, out = [], []
    for k in keys:
        hit = None
        for gi, g in enumerate(groups):
            if judge(k, g) or (single_pass and assonant(k, g)):
                hit = gi
                break
        if hit is None:
            groups.append(k)
            hit = len(groups) - 1
        out.append(hit)
    # unhashable/None keys never merge: give each None its own letter
    fixed, nxt, seen = [], 0, {}
    for k, g in zip(keys, out):
        if k is None:
            fixed.append(chr(65 + nxt)); nxt += 1
        else:
            if g not in seen:
                seen[g] = chr(65 + nxt); nxt += 1
            fixed.append(seen[g])
    return ''.join(fixed)


def spell_key(tok):
    w = tok.replace('-', '')
    return ('S', w[-2:])


def key_rejoin(tok):
    return PH.get(tok.replace('-', ''))


def key_c1(tok):
    w = ''.join(c for c, _ in runs(tok.replace('-', '')))
    return PH.get(w)


def key_first(tok):
    c = candidates(tok)
    return PH[c[0]] if c else None


def keys_ctx(toks):
    cs = [candidates(t) for t in toks]
    out = []
    for i, c in enumerate(cs):
        if len(c) <= 1:
            out.append(PH[c[0]] if c else None)
            continue
        others = [PH[x] for j, cc in enumerate(cs) if j != i for x in cc]
        pick = next((x for x in c if PH[x] in others), c[0])
        out.append(PH[pick])
    return out


def run():
    truth = {n: letters([PH[w] for w in intended]) for n, _, intended in STANZAS}
    rows = {'S': [], 'P-rejoin': [], 'P-c1': [], 'P-first': [], 'P-ctx': [], 'P-ctx-1pass': [], 'P-flag': []}
    flagged_tokens, flagged_stanzas = 0, []
    print(f"{'stanza':34s} truth  " + ' '.join(f'{k:>11s}' for k in rows))
    for name, toks, intended in STANZAS:
        res = {
            'S': letters([spell_key(t) for t in toks]),
            'P-rejoin': letters([key_rejoin(t) for t in toks]),
            'P-c1': letters([key_c1(t) for t in toks]),
            'P-first': letters([key_first(t) for t in toks]),
            'P-ctx': letters(keys_ctx(toks)),
            'P-ctx-1pass': letters(keys_ctx(toks), single_pass=True),
        }
        amb = [t for t in toks if len(candidates(t)) > 1]
        flagged_tokens += len(amb)
        if amb:
            res['P-flag'] = 'FLAG'
            flagged_stanzas.append(name)
        else:
            res['P-flag'] = letters([key_first(t) for t in toks])
        for k, v in res.items():
            rows[k].append(v == truth[name] if v != 'FLAG' else None)
        print(f"{name:34s} {truth[name]:5s}  " + ' '.join(f'{res[k]:>11s}' for k in rows))
    print()
    score = {}
    for k, v in rows.items():
        right = sum(1 for x in v if x is True)
        wrong = sum(1 for x in v if x is False)
        flag = sum(1 for x in v if x is None)
        score[k] = (right, wrong, flag)
        print(f'{k:12s} right {right}/{len(v)} wrong {wrong} flagged {flag}')
    print('candidates:', {t: candidates(t) for _, toks, _ in STANZAS for t in toks if len(candidates(t)) != 1 or t.replace('-', '') not in PH})
    n = len(STANZAS)
    ok = (score['P-flag'][1] == 0 and score['P-rejoin'][1] >= 3 and score['S'][1] >= 2
          and score['P-ctx'][1] >= 1)
    verdict = 'PASS' if ok else 'FAIL'
    print(f"RESULT: {verdict} of {n} stanzas wrong: spelling {score['S'][1]}, phonetic rejoin-only {score['P-rejoin'][1]}, "
          f"collapse-to-1 {score['P-c1'][1]}, first-candidate {score['P-first'][1]}, context tie-break {score['P-ctx'][1]}, "
          f"flag-ambiguous {score['P-flag'][1]} (flagged {score['P-flag'][2]} stanzas, {flagged_tokens} tokens)")


if __name__ == '__main__':
    run()
