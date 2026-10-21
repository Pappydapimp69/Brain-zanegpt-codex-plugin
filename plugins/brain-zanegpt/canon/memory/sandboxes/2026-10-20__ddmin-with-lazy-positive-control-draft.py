# ddmin over config items for a "poll never succeeds" failure with TWO independent
# sufficient causes (broken predicate item P, starved capture item S), judged
# through a positive control whose fidelity is parameterised.
FIELDS_REAL = {"id", "text", "ts"}
def capture(items, starved):           # upstream layer: real output fidelity
    return set(FIELDS_REAL) if not starved else set()
def predicate(state, broken):          # checks id+ts; broken variant checks a field never produced
    need = {"id", "ts"} if not broken else {"id", "ts", "zz"}
    return need <= state
def fails(items, control_fields=None):
    broken = "P" in items; starved = "S" in items
    state = capture(items, starved) if control_fields is None else set(control_fields)
    return not predicate(state, broken)
def ddmin(items, test):
    n = 2
    items = list(items)
    while len(items) >= 2:
        sz = max(1, len(items) // n); chunks = [items[i:i+sz] for i in range(0, len(items), sz)]
        reduced = False
        for c in chunks:                       # try subset
            if test(c): items, n, reduced = c, 2, True; break
        if not reduced:
            for c in chunks:                   # try complement
                comp = [x for x in items if x not in c]
                if comp and test(comp): items, n, reduced = comp, max(n-1, 2), True; break
        if not reduced:
            if n >= len(items): break
            n = min(len(items), n*2)
    return items
base = ["a","b","P","c","S","d"]
# S1: real pipeline, two independent causes: ddmin returns ONE
m1 = ddmin(base, lambda c: fails(c)); rest = [x for x in base if x not in m1]
m2 = ddmin(rest, lambda c: fails(c))
print("S1 first minimal", m1, "after delete+rerun", m2)
# S2: positive control = synthetic state; faithful control (id,text,ts) -> predicate passes unless broken
def verdict(control):                  # does a healthy-input control still fail the predicate?
    return predicate(set(control), broken=("P" in base))
faithful = verdict(FIELDS_REAL); lazy = verdict({"id"})
print("S2 control verdict faithful(predicate ok?)", faithful, "lazy(predicate ok?)", lazy)
# S3 BREAK: with predicate NOT broken, lazy control still reports predicate broken (false blame)
def verdict_ok_predicate(control): return predicate(set(control), broken=False)
print("S3 predicate healthy: faithful ->", verdict_ok_predicate(FIELDS_REAL), " lazy ->", verdict_ok_predicate({"id"}))
ok = (m1 != m2 and len(m1) == 1 and len(m2) == 1 and sorted(m1+m2) == ["P","S"]
      and verdict_ok_predicate(FIELDS_REAL) is True and verdict_ok_predicate({"id"}) is False)
print(("RESULT: PASS" if ok else "RESULT: FAIL"), "ddmin stalls on one of two causes (%s then %s); lazy control blames a healthy predicate" % (m1, m2))
