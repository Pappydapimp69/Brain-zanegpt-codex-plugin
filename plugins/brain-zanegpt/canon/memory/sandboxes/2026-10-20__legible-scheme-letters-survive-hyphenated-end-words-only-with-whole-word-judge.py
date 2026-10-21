import itertools
# word -> (hyphenated form, true rhyme class)
V={'time':('ti-me','IME'),'prime':('pri-me','IME'),'day':('day','AY'),'away':('a-way','AY'),'desire':('de-sire','IRE'),'fire':('fi-re','IRE'),'higher':('hi-gher','IRE'),'low':('low','OH')}
def whole(h): return V_by_h[h][1]
V_by_h={h:(w,c) for w,(h,c) in V.items()}
plain_cls={w:c for w,(h,c) in V.items()}
def last_seg_class(h):
    seg=h.split('-')[-1]
    # judge by spelling of the last segment: its final 2 letters
    return seg[-2:]
def letters(classes):
    """two-pass: groups of 2+ get capital letters in order of appearance, singletons 'x'"""
    out=[];m={};n=0
    for c in classes:
        if classes.count(c)<2: out.append('x'); continue
        if c not in m: m[c]=chr(65+n); n+=1
        out.append(m[c])
    return ''.join(out)
def legible(classes,scheme):  # each letter names exactly one true class
    d={}
    for c,l in zip(classes,scheme):
        if l=='x': continue
        d.setdefault(l,set()).add(c)
    return all(len(v)==1 for v in d.values())
words=list(V); N=0; wh_same=ls_same=ls_illegible=wh_illegible=0
for st in itertools.product(words,repeat=4):
    N+=1
    truth=[plain_cls[w] for w in st]
    plain=letters(truth)
    hy=[V[w][0] for w in st]
    wh=letters([whole(h) for h in hy]); ls=letters([last_seg_class(h) for h in hy])
    wh_same+= wh==plain; ls_same+= ls==plain
    wh_illegible+= not legible(truth,wh); ls_illegible+= not legible(truth,ls)
print('stanzas',N,'whole-word same as plain',wh_same,'last-seg same',ls_same,'whole illegible',wh_illegible,'last-seg illegible',ls_illegible)
ok=wh_same==N and wh_illegible==0 and ls_same<N and ls_illegible==0  # corrected after run 2: miss splits groups, never merges them
print('RESULT: %s whole-word %d/%d identical, 0 illegible; last-segment %d/%d identical, %d illegible'%('PASS' if ok else 'FAIL',wh_same,N,ls_same,N,ls_illegible))
