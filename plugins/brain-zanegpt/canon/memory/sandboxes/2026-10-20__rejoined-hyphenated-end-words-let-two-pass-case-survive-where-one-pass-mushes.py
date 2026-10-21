import itertools
# word -> (perfect rime, vowel)
D={'night':('ait','a'),'light':('ait','a'),'time':('aim','a'),'mine':('ain','a'),'sky':('ai','a'),
   'ground':('ound','o'),'sound':('ound','o'),'road':('oad','o'),'home':('ohm','o'),'bone':('ohn','o'),
   'sea':('ee','e'),'free':('ee','e'),'dream':('eem','e'),'seen':('een','e')}
HY={'night':'ni-ght','light':'li-ght','ground':'grou-nd','sound':'sou-nd','free':'fre-e','sea':'se-a','dream':'drea-m'}
def rejoin(w): return w.replace('-','')
def one_pass(ws):  # any rhyme type (perfect or vowel) claims a letter
    ws=[rejoin(w) for w in ws];out=['']*4;n=0
    for i in range(4):
        if out[i]: continue
        grp=[j for j in range(i,4) if not out[j] and (D[ws[j]][0]==D[ws[i]][0] or D[ws[j]][1]==D[ws[i]][1])]
        L='ABCD'[n];n+=1
        for j in grp: out[j]=L
    return ''.join(out)
def two_pass(ws):
    ws=[rejoin(w) for w in ws];out=['x']*4;n=0
    for i in range(4):
        if out[i]!='x': continue
        grp=[j for j in range(i,4) if out[j]=='x' and D[ws[j]][0]==D[ws[i]][0]]
        if len(grp)>1:
            for j in grp: out[j]='ABCD'[n]
            n+=1
    m=0
    for i in range(4):
        if out[i]!='x': continue
        grp=[j for j in range(i,4) if out[j]=='x' and D[ws[j]][1]==D[ws[i]][1]]
        if len(grp)>1:
            for j in grp: out[j]='abcd'[m]
            m+=1
    return ''.join('x' if c=='x' else c for c in out)
def part(l):  # partition of lines into same-letter groups (case-insensitive), singletons dropped
    g={}
    for i,c in enumerate(l):
        if c!='x': g.setdefault(c.upper() if c.isupper() else c,[]).append(i)
    return sorted(tuple(v) for v in g.values() if len(v)>1)
def truth(ws):  # resolved groups only, uppercase; leftovers x or assonance lower
    return two_pass(ws)
words=list(D)
tot=0;op_bad=0;tp_ok=0;hy_same=0;mush=0
for c in itertools.product(words,repeat=4):
    tot+=1
    h=[HY.get(w,w) for w in c]
    if two_pass(h)==two_pass(list(c)): hy_same+=1
    t=two_pass(c)
    # real stanza has an uppercase pair and a stray assonance pair elsewhere -> one-pass must keep them distinct
    if any(ch.isupper() for ch in t) and any(ch.islower() for ch in t):
        mush+=1
        if part(one_pass(h))!=part(t): op_bad+=1
print('stanzas',tot,'two-pass hyphen==plain',hy_same,'mixed(resolved+assonance) stanzas',mush,'one-pass loses a letter in',op_bad)
# BREAK: unrejoined last-fragment judge would key 'ght','nd' etc -> not tested; instead break = raw hyphen tokens lettered
brk=[HY['night'],HY['light'],'time','mine']
print('BREAK night/light/time/mine two-pass',two_pass(brk),'one-pass',one_pass(brk))
ok=hy_same==tot and mush>0 and op_bad>0.1*mush
print(('RESULT: PASS' if ok else 'RESULT: FAIL')+' rejoined two-pass identical hyphenated vs plain %d/%d; one-pass lost a letter in %d of %d mixed stanzas (%.1f%%)'%(hy_same,tot,op_bad,mush,100*op_bad/max(mush,1)))
