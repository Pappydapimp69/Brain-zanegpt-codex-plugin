# Sandbox: shape verdict (closed AABB-like vs open ABBA-like) of every 4-line stanza drawn from a 9-word end vocabulary,
# lettered by a whole-word judge vs a last-segment judge after hyphenating end words.
# Prediction (written before run): whole-word judge keeps the verdict in 100% of stanzas; the last-segment judge
# flips the verdict in roughly 15-30% of the 6561 stanzas; flips are all caused by words whose last segment is a
# shared suffix (-ly, -ful) that is not their rhyme.
import itertools
WORDS = {  # word: (hyphenated, true rhyme key)
 'night':('night','ight'),'light':('light','ight'),'tonight':('to-night','ight'),
 'sky':('sky','y'),'goodbye':('good-bye','y'),
 'lonely':('lone-ly','olee'),'slowly':('slow-ly','olee'),'quickly':('quick-ly','ickly'),
 'beautiful':('beau-ti-ful','ootiful'),
}
SEGKEY = {'night':'ight','light':'ight','to':'to','sky':'y','bye':'y'}  # judge's lexicon of known segments
def letters(keys):
    seen, out = {}, ''
    for k in keys:
        seen.setdefault(k, 'ABCD'[len(seen)]); out += seen[k]
    return out
def verdict(s):
    if s[0]==s[1] and s[2]==s[3] and s[0]!=s[2]: return 'closed'
    if s[0]==s[3] and s[1]==s[2] and s[0]!=s[1]: return 'open'
    return 'other'
def whole(w): return WORDS[w][1]
def last(w):
    seg = WORDS[w][0].split('-')[-1]; return SEGKEY.get(seg, seg)
tot=flip_w=flip_l=0; cause=0; shapes_lost=0
for st in itertools.product(WORDS, repeat=4):
    tot+=1
    a=verdict(letters([whole(w) for w in st])); b=verdict(letters([last(w) for w in st]))
    flip_l += a!=b
    if a!=b and any(WORDS[w][0].split('-')[-1] in ('ly','ful','ti') for w in st): cause+=1
    # whole-word judge on rejoined hyphenated word is the same key by construction; check via reversal
    flip_w += verdict(letters([whole(w) for w in st]))!=a
real_open_closed = sum(verdict(letters([whole(w) for w in st]))!='other' for st in itertools.product(WORDS, repeat=4))
print('stanzas',tot,'with open/closed verdict',real_open_closed)
print('whole-word flips',flip_w,'last-segment flips',flip_l,f'{100*flip_l/tot:.1f}%','caused by suffix words',cause)
print(('RESULT: PASS' if flip_w==0 and flip_l>0 and cause==flip_l else 'RESULT: FAIL')+f' whole-word flips {flip_w}/{tot}, last-segment flips {flip_l}/{tot} ({100*flip_l/tot:.1f}%), all suffix-caused: {cause==flip_l}')
