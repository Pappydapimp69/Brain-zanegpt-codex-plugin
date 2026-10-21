import itertools
# mod = (id, priority, ops); op = (stage, kind, item, field, value)
# stage: define / patch / final. kind: set | add
MODS = {
 "base":  [("define","set","sword","dmg",10), ("define","set","sword","tags",1)],
 "boost": [("patch","add","sword","dmg",5)],
 "nerf":  [("patch","add","sword","dmg",-3)],
 "cap":   [("final","set","sword","dmg",12)],
 "dup":   [("patch","set","sword","tags",7)],   # same-field SET: built to BREAK
 "dup2":  [("patch","set","sword","tags",8)],
}
def apply(state, op):
    _, kind, item, f, v = op
    it = state.setdefault(item, {})
    if kind == "set": it[f] = v
    else:
        if f not in it: raise KeyError("patch before define")
        it[f] += v
def single_pass(order):
    s = {}
    try:
        for m in order:
            for op in MODS[m]: apply(s, op)
    except KeyError: return "CRASH"
    return repr(s)
def staged(order):
    s = {}
    for st in ("define","patch","final"):
        for m in order:
            for op in MODS[m]:
                if op[0]==st: apply(s, op)
    return repr(s)
def outcomes(names, fn):
    return {fn(p) for p in itertools.permutations(names)}
A = ["base","boost","nerf","cap"]          # additive patches only
B = A + ["dup","dup2"]                            # adds a conflicting SET patch
for label, names in (("additive",A),("with-set-conflict",B)):
    print(label, "single:", len(outcomes(names,single_pass)), "staged:", len(outcomes(names,staged)))
s1,s2 = len(outcomes(A,single_pass)), len(outcomes(A,staged))
b2 = len(outcomes(B,staged))
# tie-break scenario: equal priority, sort key priority only vs (priority,id)
pri = {"boost":1,"nerf":1,"dup":1,"dup2":1,"base":0,"cap":2}
def load_sorted(names, key):
    return staged(sorted(names, key=key))
inputs = list(itertools.permutations(B))
only_pri = {load_sorted(p, lambda m: pri[m]) for p in inputs}   # stable sort keeps input order on ties
tuple_k  = {load_sorted(p, lambda m: (pri[m], m)) for p in inputs}
print("tiebreak priority-only:", len(only_pri), "(priority,id):", len(tuple_k))
ok = s1>1 and s2==1 and b2>1 and len(tuple_k)==1 and len(only_pri)>1
print(("RESULT: PASS" if ok else "RESULT: FAIL"),
 f"additive 4-mod perms single={s1} staged={s2}; +SET conflict staged={b2}; tie sort priority-only={len(only_pri)} tuple={len(tuple_k)}")
