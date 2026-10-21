# Film cut list (edit decision list) renames a recut; a hand-typed D1 sidecar keyed by cut name drifts.
# Prediction (before run): with 1 of 8 variants renamed in the cut list, the silent hand sidecar drops it;
# if the dropped variant is the true IPM*D1 winner the pick changes (to the runner-up), in 1 of 8 rename
# choices only that are winner (so 1/8 flips). A derived join (by stable id) never flips; a count check
# on the join (len(joined) == len(variants)) catches 8/8 renames loudly.
IPM = {"v%d"%i: x for i,x in enumerate([9.0,7.5,8.2,6.1,10.4,7.0,8.8,6.6])}
D1  = {"v%d"%i: x for i,x in enumerate([0.22,0.30,0.26,0.31,0.17,0.29,0.21,0.28])}
cut_list = {"v%d"%i: "cut_%d"%i for i in range(8)}          # film EDL: stable id -> cut name
sidecar  = {cut_list[k]: D1[k] for k in D1}                  # hand-typed, keyed by cut NAME
def rank_sidecar(cuts):
    rows=[(k, IPM[k]*sidecar[c]) for k,c in cuts.items() if c in sidecar]   # silent drop
    return max(rows,key=lambda r:r[1])[0], len(rows)
def rank_derived():
    return max(IPM, key=lambda k: IPM[k]*D1[k])
truth = rank_derived()
flips=0; caught=0; dropped_winner=0
for victim in IPM:
    cuts = dict(cut_list); cuts[victim] = cut_list[victim]+"_r2"   # recut renamed in the EDL
    pick,n = rank_sidecar(cuts)
    flips += pick!=truth
    caught += n!=len(IPM)
    dropped_winner += victim==truth
print("true winner", truth, "flips", flips, "caught by count check", caught, "victim was winner", dropped_winner)
# all-renamed break case: sidecar empty -> max() on empty
cuts_all = {k:c+"_r2" for k,c in cut_list.items()}
try: rank_sidecar(cuts_all); allcase="no-error"
except ValueError: allcase="crash"
print("all renamed:", allcase)
ok = flips==1 and caught==8 and dropped_winner==1 and allcase=="crash" and truth=="v2"
print("RESULT: %s flips %d/8 (winner %s), count check catches %d/8, all-renamed %s" % ("PASS" if ok else "FAIL", flips, truth, caught, allcase))
