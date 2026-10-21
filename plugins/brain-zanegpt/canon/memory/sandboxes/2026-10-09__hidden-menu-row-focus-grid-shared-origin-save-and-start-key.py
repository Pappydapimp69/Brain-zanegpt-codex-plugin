"""Prediction (before first run): in a title menu whose Resume row exists only when THIS project has a valid save,
(1) a focus grid built from every row (display:none still matches) starts on the hidden Resume with no save and confirm does nothing;
(2) filtering by visibility fixes it, and identity asserts survive a menu reshape where index asserts break;
(3) with bare storage keys on a shared origin, a sibling project's save (other schema) changes this menu's shape, namespaced keys do not;
(4) an unconditional start-on-any-key handler starts the run on Ctrl/F11 and eats navigation, a handler that ignores modifier/function keys does not;
(5) BUILT TO BREAK: a per-node style check misses a row hidden by a hidden ANCESTOR, so the filter must test the whole chain.
Deterministic model, stdlib only; a hand-written model of DOM and storage, not a browser."""

class Node:
    def __init__(s, name, display="block", children=(), action=None):
        s.name, s.display, s.children, s.action, s.parent = name, display, list(children), action, None
        for c in s.children: c.parent = s
    def shown_own(s): return s.display != "none"
    def shown_chain(s): return s.shown_own() and (s.parent is None or s.parent.shown_chain())

def menu(has_save, wrap_hidden=False):
    resume = Node("resume", display="block" if has_save else "none", action="resume")
    new, settings = Node("new", action="new"), Node("settings", action="settings")
    rows = [resume, new, settings]
    root = Node("menu", children=rows)
    if wrap_hidden:                                  # group of rows hidden by the container
        grp = Node("group", display="none", children=[Node("debug", action="debug")])
        grp.parent = root; root.children.append(grp); rows = rows + grp.children
    return root, rows

def grid(rows, mode):
    if mode == "naive": return list(rows)                        # querySelectorAll: display:none still matches
    if mode == "own":   return [r for r in rows if r.shown_own()]  # per-node style check
    return [r for r in rows if r.shown_chain()]                  # offsetParent-like: whole chain

def press(rows, mode, keys, start_game_on_any_key=False):
    g, i, log = grid(rows, mode), 0, []
    for k in keys:
        if start_game_on_any_key: return "started-by-" + k, g[i].name
        if k == "Down": i = min(i + 1, len(g) - 1)
        elif k == "Enter": log.append(g[i].name if g[i].shown_chain() else "DEAD:" + g[i].name)
    return log, g[i].name

# storage on one shared origin; saves are (project, schema); a reader discards a foreign schema
def resume_visible(store, project, keyed_by_project, my_schema):
    key = (project + ":run") if keyed_by_project else "run"
    v = store.get(key)
    return v is not None and v == my_schema

res = {}
# S1 no save: naive grid starts on hidden Resume, Enter is dead
res["S1 naive"] = press(menu(False)[1], "naive", ["Enter"])
res["S1 filtered"] = press(menu(False)[1], "chain", ["Enter"])
# S2 identity vs index assertion across a menu reshape (save appears)
idx_ok = lambda rows, mode: grid(rows, mode)[0].name == "new"          # index 0 means 'New' only when no save
ident_ok = lambda rows, mode: any(r.name == "new" for r in grid(rows, mode))
res["S2 index assert, no save/save"] = (idx_ok(menu(False)[1], "chain"), idx_ok(menu(True)[1], "chain"))
res["S2 identity assert, no save/save"] = (ident_ok(menu(False)[1], "chain"), ident_ok(menu(True)[1], "chain"))
# S3 shared origin: sibling 'mirage' wrote schema 3; this project 'seven' uses schema 4
store = {"run": 3, "mirage:run": 3}
bare = resume_visible({"run": 4}, "seven", False, 4)     # bare key holds whatever the last writer stored
bare_foreign = resume_visible({"run": 3}, "seven", False, 4)
ns_foreign = resume_visible({"mirage:run": 3}, "seven", True, 4)
res["S3 bare-key menu shape: sibling wrote 4 / wrote 3 / namespaced foreign"] = (bare, bare_foreign, ns_foreign)
# S4 start-on-any-key vs modifier-aware handling
res["S4 any-key start, Ctrl first"] = press(menu(True)[1], "chain", ["Ctrl", "Down", "Enter"], start_game_on_any_key=True)
IGNORED = {"Ctrl", "F11", "Fn", "R+Ctrl"}
keys = [k for k in ["Ctrl", "Down", "F11", "Enter"] if k not in IGNORED]
res["S4 modifier-aware"] = press(menu(True)[1], "chain", keys)
# S5 BREAK: row hidden by hidden ancestor
res["S5 own-style filter keeps debug"] = [r.name for r in grid(menu(False, True)[1], "own")]
res["S5 chain filter"] = [r.name for r in grid(menu(False, True)[1], "chain")]
for k, v in res.items(): print(k, "->", v)

ok = (res["S1 naive"][0] == ["DEAD:resume"] and res["S1 filtered"][0] == ["new"]
      and res["S2 index assert, no save/save"] == (True, False) and res["S2 identity assert, no save/save"] == (True, True)
      and res["S3 bare-key menu shape: sibling wrote 4 / wrote 3 / namespaced foreign"] == (True, False, False)
      and str(res["S4 any-key start, Ctrl first"][0]).startswith("started-by-Ctrl") and res["S4 modifier-aware"][0] == ["new"]
      and "debug" in res["S5 own-style filter keeps debug"] and "debug" not in res["S5 chain filter"])
print("RESULT: %s naive grid dead-press=%s; identity survives reshape, index does not; bare shared key lets a sibling reshape the menu (namespaced does not); any-key start fires on Ctrl; own-style filter misses hidden-ancestor row, chain filter does not" % ("PASS" if ok else "FAIL", res["S1 naive"][0]))
