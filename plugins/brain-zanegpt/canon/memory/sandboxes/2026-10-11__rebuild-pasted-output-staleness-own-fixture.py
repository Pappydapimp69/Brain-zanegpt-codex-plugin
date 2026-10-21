"""Own fixture: a 'text-utils' library, 7 claims. Prediction (written before run):
 - evidence ratio (claims carrying an output artifact / claims) = 1.0 for pasted-real and pasted-fabricated decks, 0.0 for prose;
 - after v2 changes 3 of the 5 real behaviours, slide-only inspection finds 0 stale claims in pasted and prose decks;
 - a re-run against v2 with the stored expected output flags exactly 3 real + 1 fabricated (4); a re-baselined re-run flags 0;
 - an unrelated v2 change (function not in the deck) produces 0 flags (no false alarms)."""
def v1():
    return {
     "slug":   lambda s: "-".join(s.lower().split()),
     "trunc":  lambda s,n: s[:n],
     "pad":    lambda s,n: s.ljust(n,"."),
     "count":  lambda s: len(s.split()),
     "title":  lambda s: s.title(),
     "rev":    lambda s: s[::-1],
     "unused": lambda s: s.strip(),
    }
def v2():
    f=v1()
    f["slug"]  = lambda s: "_".join(s.lower().split())      # changed
    f["trunc"] = lambda s,n: s[:n]+"…" if len(s)>n else s    # changed
    f["count"] = lambda s: len(s.split(" "))                 # changed (double spaces)
    return f
CALLS=[("slug",("Hello  World",)),("trunc",("abcdefgh",4)),("pad",("ab",5)),("count",("a  b c",)),("title",("x y",)),
       ("rev",("abc",)),]
FAB=("pad",("zz",4),"zz..!!")   # fabricated: never produced by any version
def make_decks(lib):
    pasted=[(n,a,lib[n](*a)) for n,a in CALLS]+[FAB]
    prose=[(n,a,None) for n,a in CALLS]+[(FAB[0],FAB[1],None)]
    return pasted,prose
def ratio(deck): return sum(1 for *_,o in deck if o is not None)/len(deck)
def slide_only_stale(deck): return 0     # nothing on the slide records the version: stale claims are indistinguishable
def rerun_flags(deck,lib):
    return sum(1 for n,a,o in deck if o is not None and lib[n](*a)!=o)
pasted,prose=make_decks(v1())
r_p,r_pr=ratio(pasted),ratio(prose)
fab_only=ratio([FAB and (FAB[0],FAB[1],FAB[2])])
flags_v1=rerun_flags(pasted,v1())
flags_v2=rerun_flags(pasted,v2())
rebased=[(n,a,v2()[n](*a)) for n,a,o in pasted]; flags_rebase=rerun_flags(rebased,v2())
# real-change count among real claims
real_changed=sum(1 for n,a in CALLS if v1()[n](*a)!=v2()[n](*a))
# false-alarm control: deck citing only unchanged fns
unchanged=[(n,a,v1()[n](*a)) for n,a in CALLS if n in ("pad","title","rev")]
flags_unchanged=rerun_flags(unchanged,v2())
print(f"ratio pasted={r_p} prose={r_pr} fab_only={fab_only}; v1 rerun flags={flags_v1} (fab counts)")
print(f"real_changed={real_changed} slide_only={slide_only_stale(pasted)}/{slide_only_stale(prose)} rerun_v2={flags_v2} rebaselined={flags_rebase} unchanged_deck_v2={flags_unchanged}")
ok = r_p==1.0 and r_pr==0.0 and fab_only==1.0 and real_changed==3 and flags_v1==1 and flags_v2==4 and flags_rebase==0 and flags_unchanged==0
print("RESULT: %s ratio_pasted=%s ratio_prose=%s rerun_v2=%d rebaselined=%d false_alarms=%d"%("PASS" if ok else "FAIL",r_p,r_pr,flags_v2,flags_rebase,flags_unchanged))
