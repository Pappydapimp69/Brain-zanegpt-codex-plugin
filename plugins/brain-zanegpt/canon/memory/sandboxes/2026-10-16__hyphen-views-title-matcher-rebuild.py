# Rebuild: lyric title-drop matcher, split-on-hyphen view vs join-hyphen view. Own fixture.
import re
def norm(s): return re.sub(r"[^a-z\- ]","",s.lower())
def split_view(line): return re.sub(r"-"," ",norm(line)).split()
def join_view(line): return re.sub(r"-","",norm(line)).split()
def has(tokens,title):
    t=title.split();n=len(t)
    return any(tokens[i:i+n]==t for i in range(len(tokens)-n+1))
titles=["midnight train","silver lining","paper moon","glass house","open road"]
stutter=["mi-mi-midnight train to nowhere","I saw the sil-silver lining","pa-paper moon above","g-glass house on fire","o-open road ahead"]
timing=["mid-night train rolls by","sil-ver lin-ing in the sky","pa-per moon tonight","glass house on the hill".replace("glass house","glass hou-se"),"o-pen road ahead"]
plain=["the midnight train leaves","a silver lining waits","paper moon rising","a glass house stands","the open road calls"]
neg=["a midnight snack","silver spoon","paper plane","glass of wine","open door"]
def rate(lines,view):
    hit=0
    for l,t in zip(lines,titles):
        if has(view(l),t): hit+=1
    return hit
def fp(view): return sum(1 for l in neg for t in titles if has(view(l),t))
def both(l): return split_view(l),join_view(l)
r={}
for name,v in(("split",split_view),("join",join_view)):
    r[name]=(rate(stutter,v),rate(timing,v),rate(plain,v),fp(v))
both_hits=sum(1 for lines in(stutter,timing,plain) for l,t in zip(lines,titles) if any(has(x,t) for x in both(l)))
print("split (stutter,timing,plain,fp)",r["split"]);print("join",r["join"]);print("both found",both_hits,"/15")
ok = r["split"][0]==5 and r["split"][1]==0 and r["join"][1]==5 and r["join"][0]<=1 and both_hits==15 and r["split"][3]==0 and r["join"][3]==0
print("RESULT: %s split stutter/timing=%d/%d join stutter/timing=%d/%d both=%d/15 fp=%d/%d"%("PASS" if ok else "FAIL",r["split"][0],r["split"][1],r["join"][0],r["join"][1],both_hits,r["split"][3],r["join"][3]))
