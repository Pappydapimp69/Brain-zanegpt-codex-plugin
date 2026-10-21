"""Blind rebuild of seven E84 (when merging keyed sets, namespace every key, not
just the fallback bucket). Own fixture: two plugin registries that group
commands by category. A = {audio:[mute,vol], ui:[zoom], other:[a_misc]},
B = {audio:[record], net:[ping,trace], other:[b_misc1,b_misc2]}. In B 'audio'
means recording (different owner). Merge into one dict of category->members.
Misfiled = a member whose merged group contains a member from the other source.
PREDICTION (before running): naive merge misfiles members in both 'audio' and
'other'; renaming only the fallback ('A:other','B:other') still misfiles the
'audio' members (3 of 9); namespacing every key misfiles 0; with no shared real
ids a naive merge misfiles only fallback members, and fallback-only fixes it.
Break scenario: the shared id is a deliberate JOIN (both registries' 'net' mean
the same thing and should merge). Full namespacing then SPLITS a group that
should be one: 'namespace everything' needs an explicit join list.
"""
import sys
print("python", sys.version.split()[0])
def merge(A, B, mode, joins=()):
    out = {}
    for src, R in (("A", A), ("B", B)):
        for k, ms in R.items():
            if mode == "naive" or (mode == "fallback" and k != "other") or k in joins: key = k
            else: key = f"{src}:{k}"
            out.setdefault(key, []).extend((src, m) for m in ms)
    return out
def misfiled(out):
    return sum(1 for g in out.values() for s, _ in g if any(s2 != s for s2, _ in g))
A = {"audio": ["mute", "vol"], "ui": ["zoom"], "other": ["a_misc"]}
B = {"audio": ["record"], "net": ["ping", "trace"], "other": ["b_misc1", "b_misc2"]}
n = sum(len(v) for v in A.values())+sum(len(v) for v in B.values())
r = {m: misfiled(merge(A, B, m)) for m in ("naive", "fallback", "full")}
print("shared real id:", r, "of", n)
B2 = {"rec": ["record"], "net": ["ping", "trace"], "other": ["b_misc1", "b_misc2"]}
r2 = {m: misfiled(merge(A, B2, m)) for m in ("naive", "fallback", "full")}
print("no shared real id:", r2)
# break: deliberate join on 'net'
A3 = dict(A, net=["dns"])
full = merge(A3, B, "full"); split = "A:net" in full and "B:net" in full
joined = merge(A3, B, "full", joins=("net",)); ok_join = len(joined["net"]) == 3 and misfiled({k: v for k, v in joined.items() if k != "net"}) == 0
print("break: full namespacing splits intended join 'net':", split, "| explicit join list fixes it:", ok_join)
ok = r["naive"] > 0 and r["fallback"] == 3 and r["full"] == 0 and r2["naive"] > 0 and r2["fallback"] == 0
print(f"RESULT: {'PASS' if ok else 'FAIL'} shared id: naive {r['naive']}/{n}, fallback-only {r['fallback']}/{n}, full {r['full']}; no shared id: fallback-only {r2['fallback']}; full namespacing splits an intended join={split}")
