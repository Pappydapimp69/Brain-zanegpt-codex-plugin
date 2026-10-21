# Prediction (written before first run): a case/commentary/verse validates as
# irresolvable only while >=2 candidate responses stay un-critiqued AND the verse
# names no candidate. Critiquing n-1 of n responses leaks the answer by
# elimination; the planned commentary can pass while the FINISHED one fails once
# a dedupe step merges entries (opticon/E16: validate the finished artefact).
N = 8
RESP = ["speak", "silence", "shout", "bow", "strike", "walk-away", "laugh", "ask-back"]

def live(critiqued):
    return [r for r in RESP if r not in critiqued]

def resolvable(critiqued, verse):
    cands = live(critiqued)
    if len(cands) == 1:
        return True, "elimination"
    named = [r for r in cands if r in verse.split()]
    if len(named) == 1:
        return True, "verse-names-answer"
    if not cands:
        return False, "all-critiqued"
    return False, "open(%d)" % len(cands)

def proxy(critiqued):  # finger: how many responses got commentary
    return len(critiqued)

res = []
# 1 canonical: 5 critiqued, verse images only
c1 = RESP[:5]; r1 = resolvable(c1, "the moon in the bucket spills")
res.append(("canonical", r1[0] is False)); print("1 canonical", r1, "proxy", proxy(c1))
# 2 BREAK: 7 of 8 critiqued (more commentary = thoroughness proxy) -> leaks
c2 = RESP[:7]; r2 = resolvable(c2, "the moon in the bucket spills")
res.append(("overcritique-leaks", r2 == (True, "elimination"))); print("2 overcritique", r2, "proxy", proxy(c2))
# 3 verse names the lone survivor among 3 live -> leaks via verse
c3 = RESP[:5]; r3 = resolvable(c3, "only laugh remains of the moon")
res.append(("verse-leak", r3 == (True, "verse-names-answer"))); print("3 verse", r3)
# 4 plan vs finished: planned 5 critiques, generator dedupe adds 2 aliases
planned = RESP[:5]; finished = planned + ["laugh", "ask-back"]
rp = resolvable(planned, "moon bucket"); rf = resolvable(finished, "moon bucket")
res.append(("plan-passes-finished-fails", rp[0] is False and rf[0] is True))
print("4 plan", rp, "finished", rf)
# 5 proxy decoupling: proxy rises 5->6 with true open count 3->2 still safe, 7 flips
sweep = [(k, len(live(RESP[:k])), resolvable(RESP[:k], "x")[0]) for k in range(0, 9)]
print("5 sweep (critiqued, live, resolvable):", sweep)
flip = min(k for k, l, r in sweep if r)
res.append(("flip-at-n-1", flip == N - 1 or (flip == N - 1)))
print("flip at critiqued =", flip)
ok = all(v for _, v in res)
print("RESULT: %s koan irresolvability holds to %d/%d critiqued; flips at n-1=%d; verse naming and post-dedupe commentary also leak; %d/%d checks"
      % ("PASS" if ok else "FAIL", flip - 1, N, flip, sum(v for _, v in res), len(res)))
