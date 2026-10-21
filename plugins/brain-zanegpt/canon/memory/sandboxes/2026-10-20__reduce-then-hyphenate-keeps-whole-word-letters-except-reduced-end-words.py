import re, itertools
# rime dictionary (phonetic judge keyed on the whole word)
R={'night':'ait','light':'ait','tonight':'ait','sky':'ai','fly':'ai','high':'ai','go':'oh','know':'oh','slow':'oh',
   'gonna':'ona','wanna':'ona','donna':'ona','town':'own','down':'own','home':'ohm','alone':'own2','stay':'ay','away':'ay','day':'ay'}
SYL={'tonight':2,'away':2,'alone':2,'gonna':2,'wanna':2,'donna':2,'home':1}
HY={'tonight':'to-night','away':'a-way','alone':'a-lone','gonna':'gon-na','wanna':'wan-na','donna':'don-na'}
def syl(w):
    w=w.replace('-','')
    return SYL.get(w, 1 if w in R else {'going':2,'to':1,'the':1,'i':1,'we':1}.get(w,1))
def count(line): return sum(syl(w) for w in line.split())
def reduce(line):  # companion: going to -> gonna only before a bare verb (guard: not before 'the')
    return re.sub(r"\bgoing to (?!the\b)(?=\w)", "gonna ", line)
def hyph(line):
    ws=line.split(); ws[-1]=HY.get(ws[-1],ws[-1]); return ' '.join(ws)
def endw(line): return line.split()[-1].replace('-','')
def letters(st):  # two-pass: perfect groups first, no merging; whole-word key
    keys=[R.get(endw(l),endw(l)) for l in st]; m={};out=''
    for k in keys:
        if k not in m: m[k]='ABCD'[len(m)]
        out+=m[k]
    return out
def pipeline(st):
    s=[reduce(l) for l in st]
    s=[hyph(l) if count(l)>5 else l for l in s]
    return s
ends=['night','sky','go','town','home','day','away','alone','tonight','fly','know','down']
fills=['we are going to run','i am going to stay','we are going to the','i know we are going to','we are going to fly']
scen={}
# S1 exhaustive 4-line stanzas, end words from bank, bodies mid-line "going to <verb>"
n=bad=0;sav=0;lines=0
for combo in itertools.product(ends[:6],repeat=4):
    st=[f"we are going to run {e}" for e in combo]
    after=pipeline(st); n+=1
    if letters(st)!=letters(after): bad+=1
    for a,b in zip(st,after): sav+=count(a)-count(b.replace('-',' ')) ; lines+=1
scen['S1 mid-line going-to, 1296 stanzas']=(bad,n)
# S2 guard: 'going to the' unchanged
st=["we are going to the "+e for e in ends[:4]]
scen['S2 guard going-to-the unchanged']=(0 if pipeline(st)==[hyph(l) if count(l)>5 else l for l in st] else 1,1)
# S3 BREAK: reduced form at line END changes the rhyme word
st=["go where we are going to","the night the sky the day","what you are going to","stay and fly high"]
brk=[reduce(l) for l in st]
scen['S3 BREAK end-position going-to']=(1 if letters(st)!=letters(pipeline(st)) else 0,1)
print('lines',lines,'syllables saved/line',sav/lines)
for k,v in scen.items(): print(k,'letters-changed',v[0],'of',v[1])
print('end-position raw ends',[endw(l) for l in st],'->',[endw(l) for l in pipeline(st)])
ok=scen['S1 mid-line going-to, 1296 stanzas'][0]==0 and scen['S2 guard going-to-the unchanged'][0]==0
print(('RESULT: PASS' if ok else 'RESULT: FAIL')+' mid-line reduce+hyphenate kept letters %d/%d, saved %.2f syl/line; end-position break changed letters=%d'%(n-scen['S1 mid-line going-to, 1296 stanzas'][0],n,sav/lines,scen['S3 BREAK end-position going-to'][0]))
