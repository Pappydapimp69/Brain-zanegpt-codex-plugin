# Does the H/E/X(+F,J,stock) beat check handle a joke-to-confession callback? Deterministic, stdlib only.
# beat = (nouns, derived_from_game, level, literal, callback_of)  callback_of = index of earlier beat or None
GAME = {'ladder'}
def classify(sheet, flip_rule):
    out = []
    for i, (nouns, derived, level, literal, cb) in enumerate(sheet):
        prev_level = sheet[i-1][2] if i else 0
        new = set(nouns) - set().union(*[set(b[0]) for b in sheet[:i]]) if i else set(nouns)
        if i and new - GAME and not derived: out.append('X'); continue
        if flip_rule and cb is not None and literal and not sheet[cb][3] and set(nouns) & set(sheet[cb][0]):
            out.append('E'); continue          # figurative->literal return = explore (why is this true?)
        if i and level - prev_level > 2: out.append('J'); continue
        if i and level <= prev_level and cb is None and not derived: out.append('F'); continue
        if i and level <= prev_level: out.append('F'); continue
        out.append('H' if i else 'B')
    return out
sheets = {
 # 1: confession callback: joke ladder early (figurative), returns literal at same intensity
 'confession': ([({'ladder'},False,1,False,None),({'ladder'},True,2,False,None),({'ladder'},True,3,False,None),({'ladder'},True,3,True,0)],
                ['B','H','H','E']),
 # 2: plain flat repetition callback, no flip -> must stay F
 'flat-repeat': ([({'ladder'},False,1,False,None),({'ladder'},True,2,False,None),({'ladder'},True,2,False,1)],
                 ['B','H','F']),
 # 3: literal beat with no earlier joke to flip (cb None) -> must not get the free pass
 'orphan-literal': ([({'ladder'},False,1,False,None),({'ladder'},True,2,False,None),({'ladder'},True,2,True,None)],
                    ['B','H','F']),
 # 4: new unrelated noun disguised as a callback flip -> still X
 'new-noun-flip': ([({'ladder'},False,1,False,None),({'ladder'},True,2,False,None),({'ladder','mortgage'},False,2,True,0)],
                   ['B','H','X']),
 # 5: clean heighten sheet, flip rule must not disturb
 'clean': ([({'ladder'},False,1,False,None),({'ladder'},True,2,False,None),({'ladder'},True,3,False,None)],
           ['B','H','H']),
}
tot = {False: 0, True: 0}
for name, (sheet, want) in sheets.items():
    for fr in (False, True):
        got = classify(sheet, fr)
        hit = sum(g == w for g, w in zip(got, want)); tot[fr] += hit
        print(name, 'flip_rule=%s' % fr, got, 'want', want, '%d/%d' % (hit, len(want)))
n = sum(len(v[1]) for v in sheets.values())
print('exact without rule %d/%d, with rule %d/%d' % (tot[False], n, tot[True], n))
ok = tot[False] == n - 1 and tot[True] == n
print('RESULT: %s check without callback-flip rule mislabels the confession return as F (%d/%d); adding the rule gives %d/%d with the three break cases still F/F/X'
      % ('PASS' if ok else 'FAIL', tot[False], n, tot[True], n))
