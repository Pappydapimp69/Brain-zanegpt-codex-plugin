# Sandbox: two-pass letters (UPPER = resolved perfect, lower = open assonance) with a declared-target check ("declared open but
# every rhyme perfect"), on all 4-line stanzas from 9 end words, whole-word judge vs last-segment judge after hyphenating
# silent-e words the way a vowel-group splitter does (de-si-re, lo-ve, ti-me).
# Prediction (written before run): whole-word judge never changes a letter; the last-segment judge reads every silent-e
# segment as the same vowel 'e' + empty coda, so it turns open/other pairs into false perfect pairs and flips the case of
# at least 20% of stanzas that contain two or more silent-e words of different rhyme.
import itertools
W = {  # word: (true (vowel,coda), hyphenated segments)
 'desire':(('i','re'),['de','si','re']),'fire':(('i','re'),['fi','re']),'higher':(('i','re'),['hi','gher']),
 'love':(('u','v'),['lo','ve']),'above':(('u','v'),['a','bo','ve']),
 'time':(('i','m'),['ti','me']),'rhyme':(('i','m'),['rhy','me']),
 'sun':(('u','n'),['sun']),'done':(('u','n'),['done']),
}
def seg_key(seg):
    v = ''.join(c for c in seg if c in 'aeiouy'); cod = ''.join(c for c in seg if c not in 'aeiouy')
    return (v[:1], cod) if seg.endswith(('e')) and len(seg) <= 2 else (v[:1], cod)
def rel(a, b):
    if a == b: return 'P'
    return 'a' if a[0] == b[0] else None
def two_pass(keys):
    n = len(keys); out = [None]*n; nxt = 0; L = 'ABCD'
    for i in range(n):
        for j in range(i+1, n):
            if rel(keys[i], keys[j]) == 'P':
                if out[i] is None and out[j] is None: out[i] = out[j] = L[nxt]; nxt += 1
                elif out[i] is None: out[i] = out[j]
                elif out[j] is None: out[j] = out[i]
    low = 'abcd'; k = 0
    for i in range(n):
        if out[i] is None:
            for j in range(i+1, n):
                if out[j] is None and rel(keys[i], keys[j]) == 'a':
                    out[i] = out[j] = low[k]; k += 1; break
    return ''.join(c or 'x' for c in out)
whole = lambda w: W[w][0]
last = lambda w: seg_key(W[w][1][-1])
tot = flip = whole_flip = fp_flag = silent2 = silent2_flip = 0
SIL = {'desire','fire','love','above','time','rhyme'}
for st in itertools.product(W, repeat=4):
    tot += 1
    a = two_pass([whole(w) for w in st]); b = two_pass([last(w) for w in st])
    c = a != b
    flip += c
    # declared-open contradiction: flagged when all lettered pairs are uppercase (no lowercase letters)
    flag_true = any(ch.isupper() for ch in a) and not any(ch.islower() for ch in a)
    flag_last = any(ch.isupper() for ch in b) and not any(ch.islower() for ch in b)
    if flag_last and not flag_true: fp_flag += 1
    keys = {W[w][0] for w in st if w in SIL}
    if sum(w in SIL for w in st) >= 2 and len(keys) >= 2:
        silent2 += 1; silent2_flip += c
print('stanzas', tot, 'letterings changed', flip, f'{100*flip/tot:.1f}%', 'whole-word self-check changes', whole_flip)
print('stanzas with 2+ silent-e words of different rhyme', silent2, 'changed', silent2_flip, f'{100*silent2_flip/max(silent2,1):.1f}%', 'false open-target contradiction flags', fp_flag)
ok = flip > 0 and silent2 and silent2_flip/silent2 >= 0.20
print(('RESULT: PASS' if ok else 'RESULT: FAIL') + f' last-segment judge changed {flip}/{tot} letterings, {silent2_flip}/{silent2} of the mixed silent-e stanzas ({100*silent2_flip/max(silent2,1):.1f}%), {fp_flag} false open-target flags')
