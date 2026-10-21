import re
LINES = ["I am going to leave tonight","we are going to want to stay","you are going to love the way","I am going to the store",
         "they were going to run away","she is going to try again","I am going to find a way home"]
def syl(w):
    w=w.lower().replace('-','')
    n=len(re.findall(r'[aeiouy]+',w))
    if w.endswith('e') and n>1 and not w.endswith('le'): n-=1
    return max(n,1)
def count(line): return sum(syl(w) for w in re.split(r'\s+',line.strip()))
def reduce_(line):  # going to + bare verb -> gonna ; not before 'the'
    return re.sub(r'\bgoing to (?!the\b)',"gonna ",line)
def hyph(line):  # hyphenate each word of 3+ letters at vowel-group boundary (crude)
    def h(m):
        w=m.group(0)
        return '-'.join(re.findall(r'[^aeiouy]*[aeiouy]+(?:[^aeiouy]+$)?',w)) or w
    return re.sub(r'[A-Za-z]{4,}',h,line)
pipes={'reduce':lambda l:reduce_(l),'hyph':lambda l:hyph(l),
       'reduce>hyph':lambda l:hyph(reduce_(l)),'hyph>reduce':lambda l:reduce_(hyph(l))}
def true(line):  # counted + 1 per 'going' (vowel-group counter reads going as 1; it sings as 2)
    t=line.replace('-','')
    return count(line)+len(re.findall(r'\bgoing\b',t))
base=sum(count(l) for l in LINES); tbase=sum(true(l) for l in LINES)
res={}
for k,f in pipes.items():
    out=[f(l) for l in LINES]
    res[k]=(tbase-sum(true(o) for o in out), sum('gonna' in o.replace('-','') for o in out), out)
    print(k,'saved',res[k][0],'gonna lines',res[k][1])
# break scenario: 'going to the store' must stay unreduced in every pipeline
brk=all('gonna the' not in o.replace('-','') for k in res for o in res[k][2])
print('break (going to the store kept):',brk)
# two-pass letters: rejoin hyphens before keying end word
ends=lambda ls:[re.sub(r'-','',l.split()[-1]) for l in ls]
print('end words intact after rejoin:',ends(res['reduce>hyph'][2])==ends(LINES))
ok=(res['hyph>reduce'][1]==0)  # PREDICTION: hyphen-first blocks the reduction
print('RESULT: %s reduce>hyph gonna 6/7 saved %d; hyph>reduce gonna %d saved %d; hyph alone saved %d'%('PASS' if ok else 'FAIL',res['reduce>hyph'][0],res['hyph>reduce'][1],res['hyph>reduce'][0],res['hyph'][0]))
