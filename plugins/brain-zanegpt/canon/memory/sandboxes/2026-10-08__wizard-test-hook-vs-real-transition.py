"""Sandbox: adaptive wizard (couchbound E1/E2) driven by real transition vs a
test-only state-jump hook (dog E24). Deterministic, stdlib only."""
CORE = ["kind", "pair", "desire", "disruption", "stakes"]
def route(a):
    r = list(CORE)
    if "place" not in a.get("kind", ""): r.append("place")
    if "vs" not in a.get("disruption", ""): r.append("opposition")
    return r + ["choice", "ending"]

class Wizard:
    def __init__(s): s.ans = {}; s.derived = {}; s.overlay = True; s.log = []
    def view(s):  # what a player sees: route + derived labels + overlay
        return (tuple(route(s.ans)), tuple(sorted(s.derived.items())), s.overlay)
    # REAL transition: commit, invalidate downstream, recompute derived, hide overlay
    def commit(s, key, val):
        r = route(s.ans); i = r.index(key) if key in r else len(r)
        for k in r[i + 1:]: s.ans.pop(k, None)
        s.ans[key] = val
        s.derived = {k: "label:" + v for k, v in s.ans.items()}
        s.overlay = False
    # TEST hook: sets answers directly (fast), no invalidation/derived/overlay
    def force(s, **kw): s.ans.update(kw)
    def finalize(s, p1=None, p2=None):
        pool = ["run", "hide", "fight"]
        p1 = p1 or pool[0]; p2 = p2 or [x for x in pool if x != p1][0]
        return p1, p2

def fresh(ans):  # oracle: build state from final answers via real transitions only
    w = Wizard()
    for k in route(ans):
        if k in ans: w.commit(k, ans[k])
    return w

seq = [("kind", "fable place"), ("pair", "a+b"), ("desire", "home"), ("disruption", "storm vs crew"),
       ("stakes", "boat"), ("choice", "stay"), ("ending", "calm")]
# S1 real path with backtrack: change kind (drops need for place), then compare to oracle
w = Wizard()
for k, v in seq: w.commit(k, v)
w.commit("disruption", "storm")           # upstream answer changes -> 'opposition' now required, downstream cleared
s1_ok = w.view()[:2] == fresh(w.ans).view()[:2] and "choice" not in w.ans
print("S1 real backtrack == fresh rebuild:", s1_ok, "| stale downstream gone:", "choice" not in w.ans)
# S2 hook path: force answers, state asserts pass, view diverges
h = Wizard(); h.force(**dict(seq[:5]))
state_assert = route(h.ans) == route(fresh(h.ans).ans)
print("S2 hook: route assertion passes:", state_assert, "| derived labels empty:", h.derived == {}, "| overlay still up:", h.overlay)
# S3 hook then backtrack via hook: stale downstream survives
h.force(choice="stay", ending="calm"); h.force(disruption="storm")
print("S3 hook backtrack keeps stale choice/ending:", "choice" in h.ans and "ending" in h.ans)
# S4 fix: hook delegates to commit -> equals oracle
f = Wizard()
for k, v in seq[:5]: f.commit(k, v)
f.commit("disruption", "storm")
print("S4 hook via real transition == oracle:", f.view() == fresh(f.ans).view())
# S5 BREAK: invalidation of answers but derived cache not recomputed -> state-only check blind
b = Wizard()
for k, v in seq: b.commit(k, v)
stale = dict(b.derived)
for k in ["choice", "ending"]: b.ans.pop(k)          # answers cleared, derived not
print("S5 answers cleared but derived stale:", set(b.derived) - set(b.ans) == {"choice", "ending"}, "| route check passes:", route(b.ans) == route(fresh(b.ans).ans))
# S6 contrast invariant (E2) on finalize: authored agreement kept, autofill distinct
print("S6 finalize:", w.finalize(), w.finalize("run", "run"))
ok = s1_ok and state_assert and h.derived == {} and h.overlay and f.view() == fresh(f.ans).view() \
     and w.finalize()[0] != w.finalize()[1] and w.finalize("run", "run") == ("run", "run")
print(("RESULT: PASS" if ok else "RESULT: FAIL"),
      "state-only assertions blind to hook skipping invalidation/derived/overlay; routing hook through real transition matches fresh rebuild")
