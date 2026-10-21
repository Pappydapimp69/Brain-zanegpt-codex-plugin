"""Prediction (before run): (1) echo chain: claim A has 5 asserting sources but 1 root, claim B has 2 sources and 2 roots;
naive count ranks A>B (5 vs 2), root count ranks B>A (2 vs 1). (2) a 2-source citation cycle with no primary terminates
and yields exactly 1 pseudo-root group. (3) BREAK: a derivative missing its derived_from field is counted as its own root, so
roots inflate 1 -> 3 for a 3-source chain with two unannotated links. (4) BREAK: one primary listed under two alias names
counts as 2 roots until aliases are canonicalized, then 1. (5) BREAK: two independent roots that are both wrong still score 2:
root count measures independence, not truth. Deterministic, stdlib only, no RNG."""
def root_of(src, graph, alias=None):
    alias = alias or {}
    seen = []
    cur = src
    while True:
        cur = alias.get(cur, cur)
        if cur in seen:                      # cycle: no primary exists
            return "CYCLE:" + "|".join(sorted(seen[seen.index(cur):]))
        seen.append(cur)
        nxt = graph.get(cur)
        if nxt is None:
            return cur
        cur = nxt
def roots(srcs, graph, alias=None):
    return {root_of(s, graph, alias) for s in srcs}

# 1 echo chain vs independent
g1 = {"wiki": "blog", "forum": "wiki", "agg": "forum", "tweet": "agg"}   # blog is the root
A = ["blog", "wiki", "forum", "agg", "tweet"]; B = ["labX", "labY"]
nA, nB, rA, rB = len(A), len(B), len(roots(A, g1)), len(roots(B, g1))
print("S1 naive A=%d B=%d roots A=%d B=%d" % (nA, nB, rA, rB))
s1 = nA > nB and rA < rB
# 2 cycle
g2 = {"p": "q", "q": "p"}
r2 = roots(["p", "q"], g2); print("S2 cycle roots", r2)
s2 = len(r2) == 1
# 3 missing annotation (BREAK)
g3 = {"c": "b", "b": "a"}                     # a root; truth chain a<-b<-c
g3_missing = {"c": "b"}                       # b lost its derived_from
r3ok, r3bad = len(roots(["a", "b", "c"], g3)), len(roots(["a", "b", "c"], g3_missing))
print("S3 annotated roots=%d with a dropped link=%d" % (r3ok, r3bad))
s3 = r3ok == 1 and r3bad == 2
g3b = {}                                       # both links lost
r3b = len(roots(["a", "b", "c"], g3b)); print("S3b all unannotated roots=%d" % r3b)
s3 = s3 and r3b == 3
# 4 alias (BREAK)
g4 = {"s1": "lab-report-v1", "s2": "lab-report-final"}
alias = {"lab-report-final": "lab-report-v1"}
r4a, r4b = len(roots(["s1", "s2"], g4)), len(roots(["s1", "s2"], g4, alias))
print("S4 roots without alias map=%d with=%d" % (r4a, r4b))
s4 = r4a == 2 and r4b == 1
# 5 independence is not truth (BREAK)
truth = {"labX": False, "labY": False}
r5 = len(roots(["labX", "labY"], {})); wrong = all(not truth[s] for s in ["labX", "labY"])
print("S5 roots=%d all-wrong=%s" % (r5, wrong))
s5 = r5 == 2 and wrong
ok = s1 and s2 and s3 and s4 and s5
print("RESULT: %s echo A naive %d>%d but roots %d<%d; cycle->%d group; dropped link inflates 1->%d (all dropped %d); alias 2->1; independent-but-wrong still scores %d" % ("PASS" if ok else "FAIL", nA, nB, rA, rB, len(r2), r3bad, r3b, r5))
