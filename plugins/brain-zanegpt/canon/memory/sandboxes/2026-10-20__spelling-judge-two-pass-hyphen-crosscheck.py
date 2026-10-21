import itertools
# word: (spelling, hyphenated, perfect-rhyme sound key, vowel class for assonance)
W={'blue':('blue','blue','u','u'),'true':('true','true','u','u'),'through':('through','through','u','u'),
   'move':('move','move','uv','u'),'love':('love','love','uv2','uh'),'dove':('dove','dove','uv2','uh'),
   'stove':('stove','stove','ov','o'),'cough':('cough','cough','of','o'),'tough':('tough','tough','uf','uh'),
   'rough':('rough','rough','uf','uh'),'wan-na':('wanna','wan-na','ana','a'),'gon-na':('gonna','gon-na','ana','a')}
ws=list(W)
def sound(w): return W[w][2]
def vowel(w): return W[w][3]
def spell(w): return W[w][0][-3:]            # spelling judge: last three letters
def hyph_spell(w): return W[w][1].split('-')[-1][-3:]  # same judge on last hyphen segment
def one_pass(st,key):
    seen={};return ''.join(seen.setdefault(key(w),chr(65+len(seen))) for w in st)
def two_pass(st,perfect,assn):
    # pass 1 perfect groups; pass 2 leftover singletons join a resolved group by assonance, else own letter
    p=[perfect(w) for w in st];cnt={k:p.count(k) for k in p}
    letters={};out=[];nxt=0
    for w,k in zip(st,p):
        if cnt[k]>1 or any(cnt[perfect(x)]>1 and assn(x)==assn(w) for x in st):
            kk=k if cnt[k]>1 else next(perfect(x) for x in st if cnt[perfect(x)]>1 and assn(x)==assn(w))
        else: kk=k
        if kk not in letters: letters[kk]=chr(65+nxt);nxt+=1
        out.append(letters[kk])
    return ''.join(out)
def miss(f):
    n=b=0
    for st in itertools.product(ws,repeat=4):
        n+=1;b+=(f(st)!=truth(st))
    return b,n
truth=lambda st: two_pass(st,sound,vowel)
r={}
r['one-pass spelling']=miss(lambda st:one_pass(st,spell))
r['two-pass spelling']=miss(lambda st:two_pass(st,spell,lambda w:spell(w)[-1]))
r['two-pass spelling hyphenated']=miss(lambda st:two_pass(st,hyph_spell,lambda w:hyph_spell(w)[-1]))
r['two-pass sound (control)']=miss(lambda st:two_pass(st,sound,vowel))
for k,(b,n) in r.items(): print('%-30s miss %d/%d = %.1f%%'%(k,b,n,100*b/n))
pc=lambda k:100*r[k][0]/r[k][1]
ok=pc('two-pass spelling')>20 and r['two-pass sound (control)'][0]==0 and pc('two-pass spelling hyphenated')>20
print('RESULT: %s two-pass lettering under a spelling judge still misses %.1f%% (hyphenated %.1f%%, one-pass %.1f%%); sound judge 0%%'%('PASS' if ok else 'FAIL',pc('two-pass spelling'),pc('two-pass spelling hyphenated'),pc('one-pass spelling')))
