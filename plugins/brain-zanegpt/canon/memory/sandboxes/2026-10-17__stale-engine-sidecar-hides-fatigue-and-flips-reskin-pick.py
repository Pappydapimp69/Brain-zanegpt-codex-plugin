# Choose between 8 reskins of the best comic engine and a diverse batch of 8 engines. Reskin k-th repeat is worth strength*(1-f)^k.
# The decision counts repeats per engine through a hand-kept sidecar {variant_name: engine}; reskins added after the sidecar
# was written are missing from it, so a missing name falls back to "its own engine" (0 repeats, no fatigue).
STR = [1.00, .82, .76, .70, .66, .62, .58, .55]       # engine strengths, engine 0 is the best
def true_values(f):
    reskin = sum(STR[0]*(1-f)**k for k in range(8))/8
    diverse = sum(STR)/8
    return reskin, diverse
def believed_reskin(f, sidecar_cover):
    # sidecar maps the first `sidecar_cover` reskin names to engine 0; the rest look like unique engines with fresh strength 1.0 each
    tot = 0.0
    for k in range(8):
        tot += STR[0]*(1-f)**k if k < sidecar_cover else STR[0]
    return tot/8
def pick(f, cover):
    r, d = true_values(f); b = believed_reskin(f, cover)
    return ("reskin" if b > d else "diverse"), ("reskin" if r > d else "diverse"), r, d
rows = []
# threshold where truth flips
fs = [i/1000 for i in range(0, 300)]
thr = next(f for f in fs if true_values(f)[0] <= true_values(f)[1])
print(f"true break-even fatigue f* = {thr:.3f}")
bad = {}
for cover in (8, 7, 6, 4, 0):                                # 8 = sidecar up to date; 0 = sidecar fully stale
    wrong = [f for f in fs if pick(f, cover)[0] != pick(f, cover)[1]]
    regret = max((true_values(f)[1]-true_values(f)[0] for f in wrong), default=0.0)
    bad[cover] = (len(wrong), round(min(wrong), 3) if wrong else None, round(regret, 3))
    print(f"sidecar covers {cover}/8 reskins: wrong picks at {len(wrong)} of {len(fs)} fatigue values, first wrong f={bad[cover][1]}, max regret {bad[cover][2]}")
# derived grouping (engine field on each record) = cover 8 equivalent
ok = bad[8][0] == 0 and bad[0][0] > 0 and bad[7][0] > 0 and all(bad[c][0] >= bad[c2][0] for c, c2 in ((7, 8), (6, 7), (4, 6), (0, 4))) and bad[0][1] >= thr
ok &= all(f >= thr for f in fs if pick(f, 0)[0] != pick(f, 0)[1])      # wrong picks only above break-even, always toward reskin
print("RESULT: %s stale sidecar over-picks reskin only above break-even f*=%.3f: wrong fatigue values out of %d = cover7 %d, cover6 %d, cover4 %d, cover0 %d, cover8 or derived 0; one missing name already costs max regret %.3f" % ("PASS" if ok else "FAIL", thr, len(fs), bad[7][0], bad[6][0], bad[4][0], bad[0][0], bad[7][2]))
