"""Blind rebuild of brain-pitch E3 (merging two id-keyed node arrays into one
clusters{} object: a shared fallback id 'other' silently double-counts into
both counters; namespace or make the fallback unreachable).
Own fixture: ideas from 7 header tokens (one, 'UI-UX', unmapped -> fallback),
memory nodes from 5 tags with its own 'other'. Counts: ideas 300 total (UI-UX 40),
memory 200 total (other 25). Three merge semantics, because the claim names the
symptom but not the merge code: ACCUMULATE (clusters[id].total += n.total),
OVERWRITE (clusters[id] = n), FIRST-WINS (setdefault). Counters sum
clusters[id].total over each source's own id list, as the claim says.
PREDICTION (written before running): ACCUMULATE inflates BOTH totals by the
other source's fallback count (ideas 325, memory 240) - the claim's 'merged,
not dropped'; OVERWRITE and FIRST-WINS do NOT double count: one total is right
and the other shows the wrong bucket (could read high or low), i.e. 'silently
dropped' - so the claim's mechanism is specific to accumulating merges;
per-source namespacing and an exhaustive mapping each give 300 / 200 under all
three semantics.
"""
import sys
print("python", sys.version.split()[0])
IDEA_TOK = {"GAME": 80, "AUDIO": 50, "UI-UX": 40, "SEARCH": 30, "WRITING": 45, "CODE": 35, "ART": 20}
MAPPED = {"GAME": "game", "AUDIO": "audio", "SEARCH": "search", "WRITING": "writing", "CODE": "code", "ART": "art"}
MEM = {"testing": 70, "state": 40, "audio": 35, "save": 30, "other": 25}
def idea_nodes(mapping, fb):
    out = {}
    for t, n in IDEA_TOK.items():
        k = mapping.get(t, fb); out[k] = out.get(k, 0) + n
    return [{"id": k, "total": v} for k, v in out.items()]
def mem_nodes(prefix=""):
    return [{"id": prefix + k, "total": v} for k, v in MEM.items()]
def merge(a, b, sem):
    cl = {}
    for n in a + b:
        if sem == "accumulate":
            cl.setdefault(n["id"], {"total": 0})["total"] += n["total"]
        elif sem == "overwrite": cl[n["id"]] = dict(n)
        else: cl.setdefault(n["id"], dict(n))
    return cl
def counters(a, b, cl):
    return sum(cl[n["id"]]["total"] for n in a), sum(cl[n["id"]]["total"] for n in b)
true = (sum(IDEA_TOK.values()), sum(MEM.values()))
# NOTE: 'audio' is a real shared id here too - a second collision the claim did not mention
res = {}
for sem in ("accumulate", "overwrite", "first"):
    I, M = idea_nodes(MAPPED, "other"), mem_nodes()
    res[(sem, "naive")] = counters(I, M, merge(I, M, sem))
    I, M = idea_nodes(MAPPED, "idea-other"), mem_nodes()
    res[(sem, "fallback-ns")] = counters(I, M, merge(I, M, sem))
    I = [{"id": "idea:" + n["id"], "total": n["total"]} for n in idea_nodes(MAPPED, "other")]; M = mem_nodes("mem:")
    res[(sem, "full-ns")] = counters(I, M, merge(I, M, sem))
    I, M = idea_nodes(dict(MAPPED, **{"UI-UX": "ui"}), "other"), mem_nodes()
    res[(sem, "exhaustive")] = counters(I, M, merge(I, M, sem))
for k, v in res.items(): print(f"{k[0]:10s} {k[1]:12s} ideas {v[0]:3d} memory {v[1]:3d}  (true {true[0]}/{true[1]})")
acc = res[("accumulate", "naive")]
c1 = acc[0] > true[0] and acc[1] > true[1]
c2 = all(not (res[(s, "naive")][0] > true[0] and res[(s, "naive")][1] > true[1]) for s in ("overwrite", "first"))
c3 = all(res[(s, "full-ns")] == true for s in ("accumulate", "overwrite", "first"))
fb_only = [s for s in ("accumulate", "overwrite", "first") if res[(s, "fallback-ns")] != true]
exh = [s for s in ("accumulate", "overwrite", "first") if res[(s, "exhaustive")] != true]
print("accumulate double-counts both:", c1, "| overwrite/first do not double-count:", c2, "| full namespacing exact:", c3)
print("fallback-only namespacing still wrong under:", fb_only, "| exhaustive mapping still wrong under:", exh, "(shared real id 'audio')")
print(f"RESULT: {'PASS' if (c1 and c2 and c3) else 'FAIL'} accumulate naive {acc[0]}/{acc[1]} vs {true[0]}/{true[1]} (both inflated); overwrite {res[('overwrite','naive')]}, first-wins {res[('first','naive')]} (one wrong, no double count); full ns exact; fallback-only/exhaustive still wrong with a shared real id under {sorted(set(fb_only+exh))}")
