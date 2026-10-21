"""Toy: a beat sheet (list of beats, each with a derived-from-game flag derived from its own text)
and a check column kept three ways: hand-typed sidecar keyed by INDEX, sidecar keyed by NAME,
and DERIVED from the beat itself. Apply edits (append, insert, delete, reorder) and count beats
whose shown verdict disagrees with the truth. Deterministic."""
def truth(b): return b["derived"]
def base():
    return [{"name": f"b{i}", "derived": d} for i, d in enumerate([1,1,0,1,0,0,1,0])]
def make_sidecars(sheet):
    return {"index": [truth(b) for b in sheet], "name": {b["name"]: truth(b) for b in sheet}}
def shown(kind, sheet, sc):
    out = []
    for i, b in enumerate(sheet):
        if kind == "index": out.append(sc["index"][i] if i < len(sc["index"]) else None)
        elif kind == "name": out.append(sc["name"].get(b["name"]))   # new beats have no entry -> None
        else: out.append(truth(b))
    return out
def wrong(kind, sheet, sc):
    return sum(1 for b, s in zip(sheet, shown(kind, sheet, sc)) if s != truth(b))
def edit_append(s): return s + [{"name": "bN", "derived": 1}]
def edit_insert_mid(s): return s[:3] + [{"name": "bN", "derived": 0}] + s[3:]
def edit_delete_first(s): return s[1:]
def edit_reorder(s): return s[::-1]
edits = [("append at end", edit_append), ("insert at position 3", edit_insert_mid), ("delete first", edit_delete_first), ("reverse order (reorder)", edit_reorder)]
res = {}
for ename, fn in edits:
    sheet0 = base(); sc = make_sidecars(sheet0); sheet1 = fn(sheet0)
    row = {k: wrong(k, sheet1, sc) for k in ("index", "name", "derived")}
    res[ename] = row
    print(f"{ename:24s} wrong verdicts: index-sidecar {row['index']}/{len(sheet1)}, name-sidecar {row['name']}/{len(sheet1)}, derived {row['derived']}/{len(sheet1)}")
ok = (all(r["derived"] == 0 for r in res.values())
      and res["append at end"]["index"] > 0                      # even an append leaves the new beat unlabeled
      and res["insert at position 3"]["index"] > res["insert at position 3"]["name"]
      and res["reverse order (reorder)"]["name"] == 0 and res["reverse order (reorder)"]["index"] > 0
      and res["delete first"]["name"] == 0)                       # BREAK: name keying survives delete and reorder
print("RESULT: PASS" if ok else "RESULT: FAIL",
      f"derived 0 wrong on all 4 edits; index sidecar wrong {res['insert at position 3']['index']} after an insert and {res['reverse order (reorder)']['index']} after a reorder; name sidecar 0 on delete/reorder but 1 missing on every added beat")
