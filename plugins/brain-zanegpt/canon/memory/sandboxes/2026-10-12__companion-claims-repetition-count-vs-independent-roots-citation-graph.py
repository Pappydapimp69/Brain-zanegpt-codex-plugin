"""Prediction (before run): on a hand-built citation graph of 4 companion-planting claims (allium-aphids, marigold-nematodes,
basil-hornworm, fennel-allelopathy), ranking claims by number of web pages repeating them puts basil-hornworm FIRST (most pages, 12),
while counting INDEPENDENT ROOTS (pages reachable from no other page's citation, i.e. sources that cite a trial/none-of-the-others)
puts it LAST with a field-trial root count of 0; marigold-nematodes (few pages, 2 trial roots) outranks it. Built to break: (a) a claim whose
pages copy WITHOUT linking (no edges) -> graph root count overstates it unless a text-shingle similarity merge is added; (b) two roots that are
really one lab (shared author) -> merge by author. Deterministic, stdlib."""
# page: (claim, cites list, kind) ; kind 'trial' = peer-reviewed field/lab trial, 'site' = gardening page
P = {}
def add(i, claim, cites, kind, text, author=None): P[i] = dict(claim=claim, cites=cites, kind=kind, text=text, author=author)
# basil-hornworm: one old gardening book quote copied around the web, 0 trials
add('b0','basil','',  'site', 'plant basil near tomatoes to repel hornworms and improve tomato flavor in the garden bed')
for i in range(1, 12):
    add(f'b{i}','basil',[f'b{i-1}'] if i % 3 else [f'b{max(0,i-2)}'],'site','plant basil near tomatoes to repel hornworms and improve tomato flavor in the garden bed')
# marigold nematodes: 2 independent trials by different groups + 1 extension page citing both
add('m0','marigold',[],'trial','Tagetes patula cover crop reduced root knot nematode galls in field trial',author='lab1')
add('m1','marigold',[],'trial','French marigold full season suppresses Meloidogyne in greenhouse soil trial',author='lab2')
add('m2','marigold',['m0','m1'],'site','extension summary marigold nematode suppression requires cover cropping')
# allium aphids: 1 trial + 3 copies citing it
add('a0','allium',[],'trial','intercropped onion garlic allicin volatiles reduce aphid host finding in trials',author='lab3')
for i in range(1,4): add(f'a{i}','allium',['a0'],'site','garlic onion intercropping reduces aphids via allicin volatiles trial')
# fennel: 1 trial, 1 site
add('f0','fennel',[],'trial','fennel root exudates anethole inhibit germination of tomato bean pea within radius',author='lab4')
add('f1','fennel',['f0'],'site','keep fennel away from tomatoes beans peas allelopathy radius')
# copy-without-links variants of fennel (break a): 6 uncited verbatim copies
for i in range(2,8): add(f'f{i}','fennel',[],'site','keep fennel away from tomatoes beans peas allelopathy radius')
claims = sorted({v['claim'] for v in P.values()})
def repetition(c): return sum(v['claim']==c for v in P.values())
def roots_graph(c):  # pages of the claim with no citation inside the claim = apparent roots
    return [k for k,v in P.items() if v['claim']==c and not [x for x in v['cites'] if x in P]]
def genuine(c):  # roots that are trials, merged by author
    return len({P[k]['author'] for k in roots_graph(c) if P[k]['kind']=='trial'})
def shingle(t,k=3): w=t.split(); return {tuple(w[i:i+k]) for i in range(len(w)-k+1)}
def jac(a,b): return len(a&b)/len(a|b) if a|b else 0
def roots_merged(c, thr=0.9):  # merge unlinked verbatim copies by text similarity
    rs=roots_graph(c); groups=[]
    for r in rs:
        s=shingle(P[r]['text'])
        for g in groups:
            if jac(s,shingle(P[g[0]]['text']))>=thr: g.append(r); break
        else: groups.append([r])
    return groups
print("claim  pages  graph-roots  trial-roots  merged-site-groups")
rep={}; gr={}; tr={}; mg={}
for c in claims:
    rep[c]=repetition(c); gr[c]=len(roots_graph(c)); tr[c]=genuine(c); mg[c]=len(roots_merged(c))
    print(f"{c:9s} {rep[c]:3d} {gr[c]:6d} {tr[c]:8d} {mg[c]:10d}")
by_rep=sorted(claims,key=lambda c:-rep[c]); by_tr=sorted(claims,key=lambda c:(-tr[c],c))
print("rank by repetition:",by_rep); print("rank by trial roots:",by_tr)
ok1 = by_rep[0]=='basil' and tr['basil']==0 and by_tr[-1]=='basil'
ok2 = tr['marigold']==2 and rep['marigold']<rep['basil']
ok3 = gr['fennel']==7 and mg['fennel']==2          # graph overstates fennel roots (7) until text-merge collapses 6 copies+... 
ok4 = tr['fennel']==1 and gr['basil']>=1
# author merge: two marigold trials from the same lab count once
P['m1']['author']='lab1'; ok5 = genuine('marigold')==1; P['m1']['author']='lab2'
print("graph roots fennel",gr['fennel'],"-> merged groups",mg['fennel'],"; same-lab marigold roots",genuine('marigold'))
print(("RESULT: PASS" if all([ok1,ok2,ok3,ok4,ok5]) else "RESULT: FAIL")+f" pages {rep}; trial roots {tr}; fennel graph roots {gr['fennel']} vs text-merged {mg['fennel']}; flags {ok1,ok2,ok3,ok4,ok5}")
