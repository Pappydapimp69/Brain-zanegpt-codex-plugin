# Sandbox: does a rule-card ceiling fixed at the start hold when the framing distance shifts mid-sketch?
# Funny beat iff 1<=severity<=distance_at_beat. Card clamps severity to its ceiling at that beat.
GO_BIG = [1, 2, 3, 4, 5, 5]
def run(dists, ceilings):
    s = f = 0
    for sev, d, c in zip(GO_BIG, dists, ceilings):
        sev = min(sev, c)
        if 1 <= sev <= d: s += sev; f += 1
    return s, f
cases = {
 "rise 2->4 static=2":   ([2,2,2,4,4,4], [2]*6),
 "rise 2->4 rewritten":  ([2,2,2,4,4,4], [2,2,2,4,4,4]),
 "drop 4->2 static=4":   ([4,4,4,2,2,2], [4]*6),
 "drop 4->2 rewritten":  ([4,4,4,2,2,2], [4,4,4,2,2,2]),
 "steady 3 static=3":    ([3]*6, [3]*6),
}
res = {k: run(*v) for k, v in cases.items()}
for k, v in res.items(): print(k, v)
ok = (res["rise 2->4 rewritten"][0] > res["rise 2->4 static=2"][0]
      and res["drop 4->2 rewritten"][1] > res["drop 4->2 static=4"][1]
      and res["steady 3 static=3"][1] == 6)
print("RESULT: %s static ceiling under-uses a rising distance and breaks on a dropping one; rewriting tracks both" % ("PASS" if ok else "FAIL"))
