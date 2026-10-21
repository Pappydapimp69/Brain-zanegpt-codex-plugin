# Sandbox: sparse lag sets, drop period lag, with vs without an always-available fallback role (role A), tick-level.
# Prediction: without fallback cutoff = largest residue-valid remaining lag (refuted case window {0,1,2}, lags 3,6,12: 12->0);
# with always-available fallback every lag is valid so cutoff = next configured lag (6). Naive next-lag is right ONLY with fallback.
from itertools import combinations
def valid_sim(L,P,W,fb):
    if fb: return True          # role A fires on any tick pair
    T=8*P+L
    return any(t%P in W and (t-L)%P in W for t in range(L,T))
def cut(pool,P,W,fb):
    v=[L for L in pool if valid_sim(L,P,W,fb)]; return max(v) if v else 0
n=nofb_bad=fb_bad=naive_nofb_wrong=naive_fb_wrong=0
for P in (12,15):
    for lo in range(1,4):
        pools=[tuple(sorted(c))+(P,) for c in combinations(range(2,P),lo)]
        for pool in pools:
            for w in range(1,6):
                W=set(range(w)); rest=[x for x in pool if x!=P]
                d={(a-b)%P for a in W for b in W}
                exp0=max([L for L in rest if L%P in d] or [0])
                g0=cut(rest,P,W,False); g1=cut(rest,P,W,True)
                n+=1; nofb_bad+= g0!=exp0; fb_bad+= g1!=max(rest)
                naive_nofb_wrong+= g0!=max(rest); naive_fb_wrong+= g1!=max(rest)
ref=(cut([3,6],12,{0,1,2},False),cut([3,6],12,{0,1,2},True))
print("cases",n,"nofb_bad",nofb_bad,"fb_bad",fb_bad,"naive_wrong_nofb",naive_nofb_wrong,"naive_wrong_fb",naive_fb_wrong,"refuted_case",ref)
ok=nofb_bad==fb_bad==naive_fb_wrong==0 and naive_nofb_wrong>0 and ref==(0,6)
print("RESULT:",("PASS" if ok else "FAIL"),n,"cases; naive next-lag wrong",naive_nofb_wrong,"without fallback, 0 with; refuted case",ref)
