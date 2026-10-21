"""Prediction (before run): with my own homophone fixture (pair/pear, week/weak, hour/our as verse end-word pairs,
plus a repeated-word verse and a post-chorus), a repetition detector keyed on WORD identity labels the three homophone
verses ABAB and the repeated-word verse XAXA and the post-chorus AAAA (5 of 5 right), while one keyed on PHONEME identity
mislabels exactly the 3 homophone verses (as XAXA... i.e. treats them as repetition) and still gets the repeated-word verse
and post-chorus right (2 of 5). Built to break: a verse mixing a true repetition with a homophone pair (fire, day, fire, way
is X A X A, but hour, sky, our, fire, ... ) must also be labelled right by word identity: [pair, bone, pear, bone] -> X(none for pair/pear)...
expected word-identity label 'ABAX' hmm: pair/pear rhyme (A,A), bone repeated (X,X) in positions 1,3 -> 'AXAX'.
Deterministic, stdlib only."""
PH = {'pair':'PEHR','pear':'PEHR','week':'WIYK','weak':'WIYK','hour':'AWR','our':'AWR','sky':'SKAY','high':'HAY',
      'door':'DOR','floor':'FLOR','stone':'STOWN','bone':'BOWN','fire':'FAYR','day':'DEY','way':'WEY','oh':'OW','go':'GOW','show':'SHOW'}
def tail(w):  # rhyme tail: phonemes from the last vowel-ish cluster; crude but deterministic: last 2 chars of phoneme string
    return PH[w][-2:]
def label(words, section, ident):
    key = (lambda w: w) if ident == 'word' else (lambda w: PH[w])
    rep = {}
    for w in words: rep[key(w)] = rep.get(key(w), 0) + 1
    out, letters, nxt = [], {}, 0
    for w in words:
        if section == 'verse' and rep[key(w)] > 1 and ident == 'word' and words.count(w) > 1:
            out.append('X'); continue
        if section == 'verse' and ident == 'phoneme' and rep[key(w)] > 1:
            out.append('X'); continue
        t = tail(w)
        if t not in letters: letters[t] = 'ABCDEFG'[nxt]; nxt += 1
        out.append(letters[t])
    return ''.join(out)
CASES = [
 ('verse', ['pair','sky','pear','high'], 'ABAB'),
 ('verse', ['week','door','weak','floor'], 'ABAB'),
 ('verse', ['hour','stone','our','bone'], 'ABAB'),
 ('verse', ['fire','day','fire','way'], 'XAXA'),
 ('post-chorus', ['oh','go','oh','show'], 'AAAA'),
]
# ITERATION 1 FAIL: my expected post-chorus label was wrong (ABAC); oh/go/show share a rhyme tail so AAAA is correct. Fixture fixed, rule untouched.
# post-chorus counts repetition, so repeated 'oh' stays a letter; letters assigned by tail
res = {}
for ident in ('word', 'phoneme'):
    res[ident] = [(label(w, s, ident), want) for s, w, want in CASES]
    print(ident, res[ident])
right = {k: sum(a == b for a, b in v) for k, v in res.items()}
# BREAK: mixed verse, true repetition (bone twice) plus a homophone pair
mix_w = label(['pair','bone','pear','bone'], 'verse', 'word'); mix_p = label(['pair','bone','pear','bone'], 'verse', 'phoneme')
print("mixed verse word:", mix_w, "phoneme:", mix_p)
ok = right['word'] == 5 and right['phoneme'] == 2 and mix_w == 'AXAX' and mix_p == 'XXXX'
print("RESULT:", "PASS" if ok else "FAIL", "word identity %d/5 right, phoneme identity %d/5 (homophone verses dropped as repetition); mixed verse word=%s phoneme=%s" % (right['word'], right['phoneme'], mix_w, mix_p))
