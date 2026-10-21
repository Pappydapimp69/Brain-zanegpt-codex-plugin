# Deterministic sandbox: two-pass rhyme lettering vs single-pass, plus scope (section) and judge (spelling) boundaries.
PH = {'day':('EY',''),'way':('EY',''),'gaze':('EY','Z'),'haze':('EY','Z'),'maze':('EY','Z'),
      'cat':('AE','T'),'hat':('AE','T'),'dog':('AO','G'),'log':('AO','G'),
      'night':('AY','T'),'light':('AY','T'),'mud':('AH','D'),'blood':('AH','D'),'flood':('AH','D'),'truck':('AH','K'),
      'shade':('EY','D'),'pain':('EY','N')}
def phon(a,b):
    if PH[a]==PH[b]: return 'perfect'
    if PH[a][0]==PH[b][0]: return 'assonance'
    return 'none'
def spell(a,b):
    if a[-2:]==b[-2:]: return 'perfect'
    return 'none'
def canon(labels):
    m={};out=''
    for l in labels:
        if l not in m: m[l]=chr(65+len(m))
        out+=m[l]
    return out
def single(words,judge,secs=None):
    lab=[]
    for i,w in enumerate(words):
        g=None
        for j in range(i):
            if secs and secs[j]!=secs[i]: continue
            if judge(words[j],w)!='none': g=lab[j];break
        lab.append(g if g is not None else ('n',i))
    return canon(lab)
def two(words,judge,secs=None):
    lab=[None]*len(words)
    for i,w in enumerate(words):   # pass 1: resolved only
        for j in range(i):
            if secs and secs[j]!=secs[i]: continue
            if judge(words[j],w)=='perfect': lab[i]=lab[j] if lab[j] is not None else ('P',j); lab[j]=lab[j] or ('P',j); lab[i]=lab[j];break
    for i,w in enumerate(words):   # pass 2: assonance among unlettered
        if lab[i] is not None: continue
        for j in range(i):
            if lab[j] is None or (lab[j][0]=='a'):
                if secs and secs[j]!=secs[i]: continue
                if judge(words[j],w)=='assonance': lab[j]=lab[j] or ('a',j);lab[i]=lab[j];break
    for i in range(len(lab)):
        if lab[i] is None: lab[i]=('n',i)
    return canon(lab)
res={}
S1=['day','gaze','way','haze']          # truth ABAB
S2=['gaze','day','haze','way']          # truth ABAB
S3=['cat','hat','dog','log']            # clean AABB
S4=['day','gaze','shade','pain']        # assonance only
for n,s,t in [('ABAB-steal',S1,'ABAB'),('ABAB-lead-assonance',S2,'ABAB'),('clean-AABB',S3,'AABB')]:
    res[n]=(single(s,phon),two(s,phon),t)
    print(n,'single',res[n][0],'two',res[n][1],'truth',t)
print('assonance-only single',single(S4,phon),'two',two(S4,phon),'(no resolved rhyme: truth ABCD-open)')
# scope: verse+chorus, chorus 'day' coincidentally matches verse 'way'
W=['day','night','way','light','day','cat','way','hat']
sec=['v']*4+['c']*4
print('scope blind',two(W,phon),'aware',two(W,phon,sec))
# judge: spelling (last 2 letters) on truck/mud/blood/flood
F=['truck','mud','blood','flood']
print('judge spelling+two',two(F,spell),'phonetic+two',two(F,phon))
ok=(res['ABAB-steal'][0]=='AAAA' and res['ABAB-steal'][1]=='ABAB' and res['ABAB-lead-assonance'][1]=='ABAB'
    and res['clean-AABB'][0]==res['clean-AABB'][1]=='AABB'
    and two(W,phon)!=two(W,phon,sec) and two(F,spell)!=two(F,phon))
print('RESULT: PASS' if ok else 'RESULT: FAIL', 'two-pass fixes steal on 2 stanzas, ties on clean stanza; scope and spelling judge remain separate failure axes')
