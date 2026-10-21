import itertools
def cd(s):
    last={};d=[]
    for i,c in enumerate(s):
        if c in last: d.append(i-last[c])
        last[c]=i
    return d
def open_count(s):  # letters appearing once so far that will repeat later: mean open rhymes per line
    seen=set();tot=0
    for i,c in enumerate(s):
        seen.add(c); tot+=sum(1 for x in seen if s[i+1:].count(x)>0)
    return tot/len(s)
def oldest_wait(s):
    mx=0
    for i,c in enumerate(s):
        if c in s[:i]: continue
        if c in s[i+1:]: mx=max(mx,s[i+1:].index(c)+1)
    return mx
S={n:n for n in ("AABB","ABAB","ABBA","AAAA","XAXA")}
for n in S: print(n,"closure",cd(n),"max",max(cd(n),default=0),"open_count",round(open_count(n),2),"oldest_wait",oldest_wait(n))
mx={n:max(cd(n),default=0) for n in S}
# exhaustive 4-line schemes: how many collide on open_count vs separate on oldest_wait
pats={"".join(chr(65+i) for i in p) for p in itertools.product(range(4),repeat=4)}
canon=set()
for p in pats:
    m={};o=""
    for c in p:
        m.setdefault(c,chr(65+len(m)));o+=m[c]
    canon.add(o)
by={}
for p in canon: by.setdefault(round(open_count(p),3),set()).add(p)
collide=sum(len(v) for v in by.values() if len(v)>1)
by2={}
for p in canon: by2.setdefault((round(open_count(p),3),oldest_wait(p)),set()).add(p)
collide2=sum(len(v) for v in by2.values() if len(v)>1)
print("4-line schemes",len(canon),"colliding on open_count alone",collide,"after adding oldest_wait",collide2)
print("RESULT:","PASS" if (mx["AABB"]==1 and mx["AAAA"]==1 and mx["ABBA"]==3 and open_count("ABAB")==open_count("ABBA") and oldest_wait("ABBA")!=oldest_wait("ABAB")) else "FAIL",
 f"max closure AABB {mx['AABB']} AAAA {mx['AAAA']} ABBA {mx['ABBA']}; ABAB and ABBA tie on open_count {open_count('ABAB')} but oldest_wait {oldest_wait('ABAB')} vs {oldest_wait('ABBA')}; {collide} of {len(canon)} schemes collide on open_count, {collide2} after oldest_wait")
