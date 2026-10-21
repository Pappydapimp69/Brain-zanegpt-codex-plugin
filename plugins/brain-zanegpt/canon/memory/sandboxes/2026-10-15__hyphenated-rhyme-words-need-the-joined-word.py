"""New half: hyphenate words to slow a rushed Suno line + the Suno builder + two-pass lettering needs a phonetic
judge. Hyphenation changes the rhyme word's spelling ('to-night'). Does two-pass lettering survive it?
Three judges: rejoin the word and look it up ('strip'), look up the hyphenated token as written ('raw'), or split on
hyphens and take the first piece ('first', a common bug). Deterministic, stdlib only."""
# a tiny phonetic lexicon: word -> (rhyme key = last vowel + coda, vowel)
LEX = {'night': ('AYT', 'AY'), 'light': ('AYT', 'AY'), 'tonight': ('AYT', 'AY'), 'bright': ('AYT', 'AY'), 'fire': ('AYR', 'AY'),
       'rain': ('EYN', 'EY'), 'chain': ('EYN', 'EY'), 'again': ('EYN', 'EY'), 'face': ('EYS', 'EY'), 'remain': ('EYN', 'EY'),
       'home': ('OWM', 'OW'), 'alone': ('OWN', 'OW'), 'heart': ('AART', 'AA'), 'apart': ('AART', 'AA'), 'dark': ('AARK', 'AA'),
       'forever': ('EHVER', 'EH'), 'together': ('EHTHER', 'EH'), 'tomorrow': ('AAROW', 'AA'), 'sorrow': ('AAROW', 'AA')}
def key(word, judge='strip'):
    w = word.lower().strip('.,!?')
    if judge == 'strip': w = w.replace('-', '')
    elif judge == 'first': w = w.split('-')[0]
    # judge 'raw': look the hyphenated token up as written
    return LEX.get(w)
def letters(last_words, two_pass=True, judge='strip'):
    ks = [key(w, judge) for w in last_words]; out = [None] * len(ks); nxt = iter('ABCDEFGH'); nxt_l = iter('abcdefgh')
    def assign(match, it, case):
        for i in range(len(ks)):
            if out[i] or not ks[i]: continue
            partners = [j for j in range(len(ks)) if j != i and ks[j] and not out[j] and match(ks[i], ks[j])]
            if partners:
                L = next(it); out[i] = L
                for j in partners: out[j] = L
    if two_pass:
        assign(lambda a, b: a[0] == b[0], nxt, 'upper')
        assign(lambda a, b: a[1] == b[1], nxt_l, 'lower')
    else:
        assign(lambda a, b: a[0] == b[0] or a[1] == b[1], nxt, 'upper')
    return ''.join(o or 'X' for o in out)
def shape(s):
    # unrhymed lines (X) never match anything, not even each other
    u = s.upper(); eq = lambda i, j: u[i] != 'X' and u[i] == u[j]
    if eq(0, 1) and eq(2, 3) and not eq(0, 2): return 'AABB'
    if eq(0, 2) and eq(1, 3) and not eq(0, 1): return 'ABAB'
    if eq(0, 3) and eq(1, 2) and not eq(0, 1): return 'ABBA'
    if eq(2, 3) and u[0] == 'X' and u[1] == 'X': return 'XXAA'
    return 'other'
# four stanzas, one per shape, each with an assonance distractor in it; lines are rushed (10-12 words)
STANZAS = {
  'AABB': ['we were running down the empty road into the night', 'every window in the town was burning with a light', 'then the morning came and brought us nothing but the rain', 'and I was holding on to you like a rusted chain'],
  'ABAB': ['we were running down the empty road into the night', 'then the morning came and brought us nothing but the rain', 'every window in the town was burning with a light', 'and I was holding on to you like a rusted chain'],
  'XXAA': ['I was standing in the doorway of the house I called my home', 'with the ashes of the summer and the embers of the fire', 'every window in the town was burning bright tonight', 'and we were dancing in the middle of the street light'],
  'ABBA': ['I gave you every broken piece of my heart', 'then the morning came and brought us nothing but the rain', 'and I was holding on to you like a rusted chain', 'until the river and the road had pulled us both apart'],
}
def front(line, n=6): w = line.split(); return ' '.join(w[-n:])
def truncate(line, n=6): return ' '.join(line.split()[:n])
HYPH = {'tonight': 'to-night', 'forever': 'for-ev-er', 'together': 'to-geth-er', 'tomorrow': 'to-mor-row', 'again': 'a-gain', 'remain': 're-main', 'alone': 'a-lone'}
def hyphenate(line): return ' '.join(HYPH.get(w, w) for w in line.split())
last = lambda lines: [l.split()[-1] for l in lines]
# stanzas whose RHYME WORDS are the long words a songwriter hyphenates to slow the line down
STANZAS = {
  'AABB': ['I keep on telling you that I will love you forever', 'and every single season we will make it through together', 'but I keep waking up into the cold and grey tomorrow', 'with nothing but the echo of a song and all the sorrow'],
  'ABAB': ['I keep on telling you that I will love you forever', 'and I keep finding ways to fall apart and start again', 'and every single season we will make it through together', 'and every bridge I ever burned is standing to remain'],
  'XXAA': ['I keep on telling you that I am fine out here alone', 'and every single morning I am walking back from home', 'but I keep waking up into the cold and grey tomorrow', 'with nothing but the echo of a song and all the sorrow'],
  'ABBA': ['I keep on telling you that I will love you forever', 'and I keep finding ways to fall apart and start again', 'and every bridge I ever burned is standing to remain', 'and every single season we will make it through together'],
}
res = {}
for judge in ('strip', 'raw', 'first'):
    kept = 0
    for name, st in STANZAS.items():
        h = [hyphenate(l) for l in st]
        L = letters(last(h), judge=judge); ok = L == letters(last(st)); kept += ok
        print(f"  judge={judge:5s} {name}: plain {letters(last(st))} hyphenated {L} {'kept' if ok else 'CHANGED'}")
    res[judge] = kept
hy_words = sum(1 for st in STANZAS.values() for l in st if '-' in hyphenate(l).split()[-1])
ok = res['strip'] == 4 and res['raw'] < 4 and res['first'] < 4
print(f"RESULT: {'PASS' if ok else 'FAIL'} {hy_words} rhyme words got hyphens; rejoining before the lookup kept {res['strip']}/4 stanzas' letters, the raw token kept {res['raw']}/4, the first fragment kept {res['first']}/4")
