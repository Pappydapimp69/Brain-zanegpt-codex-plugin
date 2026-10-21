"""Own arc classifier (valence per sentence -> sign runs -> shape). Two injected defects:
 TIE: first zero diff defaults to '+' (uninitialised previous direction). LEX: exact-match lexicon misses inflected forms.
Test on 12 stories (2 per shape) with controlled scores. Compare: first-3 spot check, overall accuracy, per-class recall.
Prediction (before run): the TIE bug misclassifies only stories whose first two sentences tie AND that fall (tragedy), so a spot check of the first 3 stories
(rags, tragedy-without-tie, hole) shows 0 change and overall accuracy drops by only 1/12; per-class recall for tragedy drops to 0.5.
LEX misses break stories only when an inflected word is a turning point or tie-breaker (iteration 1 put them at the ends and they did NOT matter: that prediction was refuted, fixture moved). Fixing TIE leaves LEX misses and vice versa (independent)."""
POS={"happy","safe","rich","win","love"}; NEG={"poor","sad","lose","fear","dead"}
def stem(w):
    if w.endswith("ier"): return w[:-3]+"y"
    if w.endswith("er"):
        b=w[:-2]; return b if b in POS|NEG else w[:-1]
    return w
def score(sent,stemming):
    sc=0
    for w in sent.split():
        w=stem(w) if stemming else w
        sc+= (w in POS)-(w in NEG)
    return sc
def shape(scores,tie_fix):
    dirs=[]; last=None if tie_fix else "+"
    for a,b in zip(scores,scores[1:]):
        d="+" if b>a else "-" if b<a else last
        if d is None: continue
        dirs.append(d); last=d
    runs=[]
    for d in dirs:
        if not runs or runs[-1]!=d: runs.append(d)
    p="".join(runs)
    return {"+":"rise","-":"fall","-+":"hole","+-":"icarus","+-+":"cinderella","-+-":"oedipus"}.get(p,"?"+p)
S=[ # (true shape, sentences)
 ("rise",["poor sad","happy","happy rich","rich love win"]),
 ("rise",["sad fear","poor","safe","safe rich love"]),
 ("fall",["rich love win","happy rich","poor","sad dead fear"]),
 ("fall",["rich happy safe","love win safe","sad","dead fear lose"]),     # first two tie (3,3)
 ("hole",["happy rich","sad","poor dead","love win safe"]),
 ("hole",["safe","fear","dead sad poor","happy rich love"]),
 ("icarus",["poor","happy","rich win love","sad dead"]),
 ("icarus",["sad","safe","love win rich","fear dead"]),
 ("cinderella",["poor","safe","dead","rich love win"]),
 ("cinderella",["sad","happy","fear","love win safe"]),
 ("oedipus",["rich","poor","love win","dead fear"]),
 ("oedipus",["happy","sad","safe rich","fear dead"]),
]
# two stories use inflected forms the exact lexicon misses
S[9]=("cinderella",["calm","safer","sad","rich love"])   # inflected form is the turning point
S[7]=("icarus",["calm","happier","sad dead"])                 # inflected form is the turning point
def evaluate(tie_fix,stemming):
    pred=[shape([score(s,stemming) for s in sents],tie_fix) for t,sents in S]
    true=[t for t,_ in S]
    acc=sum(p==t for p,t in zip(pred,true))/len(S)
    rec={}
    for c in set(true):
        idx=[i for i,t in enumerate(true) if t==c]; rec[c]=sum(pred[i]==c for i in idx)/len(idx)
    spot=sum(pred[i]==true[i] for i in range(3))/3
    return acc,rec,spot,pred
base=evaluate(True,True)                   # both fixed
bug_tie=evaluate(False,True); bug_lex=evaluate(True,False); both=evaluate(False,False)
for name,r in (("clean",base),("tie bug",bug_tie),("lex bug",bug_lex),("both",both)):
    print(f"{name:8s} acc={r[0]:.3f} spot3={r[2]:.2f} recall fall={r[1]['fall']:.1f} icarus={r[1]['icarus']:.1f} cinderella={r[1]['cinderella']:.1f}")
ok = (base[0]==1.0 and bug_tie[2]==base[2] and abs(base[0]-bug_tie[0])<=1/12+1e-9 and bug_tie[1]["fall"]==0.5
      and bug_lex[1]["icarus"]<1 and bug_lex[1]["cinderella"]<1 and both[0]>bug_lex[0])   # masking: the phantom + from the tie bug repairs the lexicon miss, so two defects score better than one
print("RESULT: %s clean=%.3f tie=%.3f lex=%.3f both=%.3f spot3_tie=%.2f fall_recall_tie=%.1f"%("PASS" if ok else "FAIL",base[0],bug_tie[0],bug_lex[0],both[0],bug_tie[2],bug_tie[1]["fall"]))
