# Prediction (before run): a labeller I write from my reading of "rhymes = same last 2 letters" scores 100% against
# a test derived from the same reading, but disagrees with a separately-defined reference (vowel+coda) on >=1/3 of fixtures.
FIX=[ # own fixtures: 4-line stanzas, last words
 ["night","light","day","way"],["cat","hat","dog","log"],["love","above","grace","place"],
 ["tree","sea","stone","bone"],["time","rhyme","fire","wire"],["rough","though","cough","low"],
 ["bear","care","here","near"],["moon","soon","tune","noon"],["sing","ring","sung","hung"],
]
def labeller_mine(ws):            # my reading: last two letters equal
    seen={};out=""
    for w in ws:
        k=w[-2:]
        if k not in seen: seen[k]=chr(65+len(seen))
        out+=seen[k]
    return out
def labeller_ref(ws):             # "existing tool": group by final vowel-group + trailing consonants
    import re
    def key(w):
        m=re.search(r'[aeiouy]+[^aeiouy]*e?$',w); return m.group(0) if m else w
    seen={};out=""
    for w in ws:
        k=key(w)
        if k not in seen: seen[k]=chr(65+len(seen))
        out+=seen[k]
    return out
# self-test: expected labels produced by the same reading (the circular check)
self_expected={i:labeller_mine(f) for i,f in enumerate(FIX)}
self_pass=sum(labeller_mine(f)==self_expected[i] for i,f in enumerate(FIX))
dis=[(f,labeller_mine(f),labeller_ref(f)) for f in FIX if labeller_mine(f)!=labeller_ref(f)]
print('self-test agree %d/%d'%(self_pass,len(FIX)))
for f,a,b in dis: print(' disagree',f,a,b)
ok=self_pass==len(FIX) and len(dis)*3>=len(FIX)
print('RESULT: %s self-test %d/%d but reference disagrees on %d/%d fixtures'%('PASS' if ok else 'FAIL',self_pass,len(FIX),len(dis),len(FIX)))
