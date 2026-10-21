"""Sandbox for ideas:SONGWRITING/rhyme-tooling/two-pass-letter-assignment-keeps-schemes-legible, ideas:SONGWRITING/rhyme/rhyme-scheme-shape-sets...,
sandbox-lyrical-composition/E7 (two-pass verified there on one stanza) and /E8 (closure distance).
PREDICTION (before first run): words are (vowel, coda) pairs. On 5 stanzas with an intended scheme, the two-pass assigner
(uppercase = same vowel AND coda; lowercase = same vowel among still-unlettered lines) recovers the intended scheme on 4, and
the one-pass vowel-only assigner on at most 2. The two-pass assigner FAILS on the all-assonance stanza (four EY words with four
codas): the lowercase pass collapses all four into 'aaaa' (mush returns one level down). A bounded fix - pair assonance one-to-one,
nearest first - recovers 'aabb'-style pairs there. Closure distance (E8) on the correct ABAB is [2,2] vs [1,1] for AABB, and the
one-pass mislabel of the day/gaze/way/daze stanza changes it from [2,2] to [1,1,1] - the mislabel changes the 'shape' reading.
ITERATION 1 OBSERVED: one-pass recovered 3/5 (prediction of at most 2 refuted - it only fails where assonance precedes a
perfect partner, 1 of 4 resolvable stanzas); assertion revised to exactly 3 after that run. Stdlib only, deterministic."""
W = {  # (vowel, coda); hand-built, CMUdict-style: day/way/say open EY; gaze/daze/phase Z coda; fate/late T coda; main/rain N coda
 'day': ('EY', ''), 'way': ('EY', ''), 'say': ('EY', ''), 'gaze': ('EY', 'Z'), 'daze': ('EY', 'Z'), 'fate': ('EY', 'T'),
 'late': ('EY', 'T'), 'main': ('EY', 'N'), 'rain': ('EY', 'N'), 'name': ('EY', 'M'), 'tame': ('EY', 'M'), 'wave': ('EY', 'V'),
 'grave': ('EY', 'V'), 'cold': ('OW', 'LD'), 'old': ('OW', 'LD'), 'home': ('OW', 'M'), 'moon': ('UW', 'N'), 'soon': ('UW', 'N'), 'stone': ('OW', 'N')}
def canon(s):  # relabel letters in order of first appearance, keeping case out of it
    m = {}; out = ''
    for ch in s:
        k = ch.lower(); m.setdefault(k, 'ABCDEFGH'[len(m)]); out += m[k]
    return out
def one_pass(words):
    lett = []; nxt = 0
    for i, w in enumerate(words):
        for j in range(i):
            if W[words[j]][0] == W[w][0]: lett.append(lett[j]); break
        else: lett.append('abcdefgh'[nxt]); nxt += 1
    return ''.join(lett)
def two_pass(words, pair_only=False):
    n = len(words); lett = [None] * n; nxt = 0
    for i in range(n):                       # pass 1: resolved rhymes claim UPPERCASE
        if lett[i]: continue
        grp = [j for j in range(i, n) if not lett[j] and W[words[j]] == W[words[i]]]
        if len(grp) > 1:
            for j in grp: lett[j] = 'ABCDEFGH'[nxt]
            nxt += 1
    for i in range(n):                       # pass 2: assonance among still-unlettered lines -> lowercase
        if lett[i]: continue
        cand = [j for j in range(i + 1, n) if not lett[j] and W[words[j]][0] == W[words[i]][0]]
        if pair_only: cand = cand[:1]        # bounded fix: one-to-one, nearest first
        if cand:
            for j in [i] + cand: lett[j] = 'abcdefgh'[nxt]
            nxt += 1
    for i in range(n):
        if not lett[i]: lett[i] = 'abcdefgh'[nxt]; nxt += 1
    return ''.join(lett)
def closure(scheme):
    last = {}; d = []
    for i, ch in enumerate(scheme.lower()):
        if ch in last: d.append(i - last[ch])
        last[ch] = i
    return d
STANZAS = [  # (words, intended)
 (['day', 'way', 'cold', 'old'], 'AABB'),
 (['day', 'gaze', 'way', 'daze'], 'ABAB'),            # reading-order assonance steals a letter in one-pass
 (['moon', 'day', 'old', 'soon'], 'ABCA'),
 (['fate', 'cold', 'late', 'old'], 'ABAB'),
 (['day', 'gaze', 'fate', 'main'], 'ABCD'),           # built to BREAK two-pass: all-assonance, no resolved rhyme
]
r1 = []; r2 = []; r3 = []
for words, want in STANZAS:
    a, b, c = canon(one_pass(words)), canon(two_pass(words)), canon(two_pass(words, True))
    r1.append(a == want); r2.append(b == want); r3.append(c == want)
    print(words, 'want', want, 'one-pass', a, 'two-pass', b, 'bounded', c, flush=True)
d_ok = closure('ABAB') == [2, 2] and closure('AABB') == [1, 1]
d_mis = closure(canon(one_pass(STANZAS[1][0])))
print('closure ABAB', closure('ABAB'), 'AABB', closure('AABB'), 'one-pass mislabel of stanza 2', canon(one_pass(STANZAS[1][0])), d_mis)
mush = canon(two_pass(STANZAS[4][0])) == 'AAAA'
ok = sum(r2) >= 4 and sum(r1) == 3 and not r2[4] and mush and d_ok and d_mis == [1, 1, 1]
print('RESULT: %s two-pass recovers %d/5 vs one-pass %d/5 vs bounded two-pass %d/5; all-assonance stanza collapses to %s; closure distance ABAB [2,2] vs one-pass mislabel %s'
      % ('PASS' if ok else 'FAIL', sum(r2), sum(r1), sum(r3), canon(two_pass(STANZAS[4][0])), d_mis))
