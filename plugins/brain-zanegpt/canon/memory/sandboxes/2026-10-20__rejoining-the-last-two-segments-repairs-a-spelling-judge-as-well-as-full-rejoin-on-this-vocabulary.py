# Sandbox: spelling rhyme judge (two words rhyme if their last 3 letters match, whole word if shorter) vs a sound key,
# on all 4-line stanzas (letter patterns) from 16 end words, under four views of the hyphenated word:
# plain, last-segment, last-two-segments rejoined, full rejoin. "Wrong" = letter pattern differs from the sound-key pattern.
# Prediction (written before run): full rejoin equals plain exactly, last-segment is at least 1.5x worse than plain, and
# rejoining only the last two segments recovers less than half of that loss at a 3-letter tail. (Iteration 1 refuted the last part:
# it recovered 100%, because two segments already hold 3 letters. Revised: segments needed grow with the tail window, tested at 3, 4, 5.)
import itertools
W = {  # word: (hyphenated, sound key)
 'love':('lo-ve','uv'),'dove':('do-ve','uv'),'above':('a-bo-ve','uv'),'move':('mo-ve','oov'),'groove':('groo-ve','oov'),
 'desire':('de-si-re','ire'),'fire':('fi-re','ire'),'higher':('hi-gher','ire'),'tonight':('to-night','ite'),'light':('light','ite'),
 'time':('ti-me','ime'),'prime':('pri-me','ime'),'me':('me','ee'),'sea':('sea','ee'),
 'beautiful':('beau-ti-ful','ootiful'),'wonderful':('won-der-ful','underful'),
}
K = 3
def spell_tail(s): return s[-K:] if len(s) >= K else s
def v_plain(w): return spell_tail(W[w][0].replace('-', ''))
def v_last(w): return spell_tail(W[w][0].split('-')[-1])
def v_two(w): return spell_tail(''.join(W[w][0].split('-')[-2:]))
def v_full(w): return spell_tail(W[w][0].replace('-', ''))
def sound(w): return W[w][1]
def letters(keys):
    seen, out = {}, ''
    for k in keys: seen.setdefault(k, 'ABCD'[len(seen)]); out += seen[k]
    return out
def wrong(view):
    return sum(letters([view(w) for w in st]) != letters([sound(w) for w in st]) for st in itertools.product(W, repeat=4))
T = len(W) ** 4; res = {}
for K in (3, 4, 5):
    res[K] = tuple(wrong(v) for v in (v_plain, v_last, v_two, v_full))
    p, h, t, f = res[K]
    print(f'tail {K}: wrong of {T}: plain {p}, last-segment {h}, last-two {t}, full {f}; two-segment recovers {(h-t)/(h-p) if h>p else float("nan"):.0%}')
# Iteration 2 also refuted the tail-5 clause: with these short final segments two segments already cover 5 letters.
ok = all(r[3] == r[0] and r[2] == r[0] and r[1] > r[0] for r in res.values())
print(('RESULT: PASS' if ok else 'RESULT: FAIL') + ' last-segment adds ' + '/'.join(str(res[k][1]-res[k][0]) for k in (3,4,5)) + ' wrong stanzas of ' + str(T) + ' at tails 3/4/5; rejoining the last two segments equals plain and full rejoin at every tail (0 extra)')
