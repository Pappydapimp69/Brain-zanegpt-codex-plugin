"""Sandbox: wizard test hook vs real transition (route hooks through commit(), diff the full view against a fresh
rebuild) x deferred-effect attribution (carry origin on deferred items; a deduping sweep keeps one origin).

Wizard steps genre -> tone -> ending. commit(step, value, origin) sets the answer, invalidates downstream answers,
recomputes derived labels and the overlay, and ARMS an idempotent deferred effect complete(step) carrying origin.
Choosing a genre makes the system autofill a default tone (origin 'auto') on the same tick. A sweep applies armed
effects: complete[step] = True and credit[origin] += 1, deduping identical effects within one sweep by key.

PREDICTION (written before the first run). Hidden assumption of the wizard rule: a full-view rebuild oracle catches
whatever a test shortcut forgot. It is wrong if a delegating hook passes that oracle while credit differs.
 S1 real play (sweep every tick): credit player 3, auto 1.
 S2 force hook (sets answers only): view oracle FAILS (control, as the wizard lesson found).
 S3 delegating hook that fast-forwards all commits and sweeps once: view oracle PASSES, final state identical,
    but credit player 2, auto 1 (the player's tone override coalesces with the autofill and loses).
 S4 delegating hook with one sweep per commit: credit equals real play.
 S5 origin-set dedupe: the single-sweep hook credits player 3 auto 1 again.
 S6 adding credit to the rebuild oracle cannot work: the rebuild has no origins, so it flags even real play.
 S7 BREAK of the ledger fix: if real play itself arms both on one tick, a replay-based credit oracle agrees with the
    bug; only an intent ledger (count of arms per origin) disagrees.
"""
STEPS = ["genre", "tone", "ending"]
DEFAULT_TONE = {"noir": "bleak", "comedy": "light"}

class Wizard:
    def __init__(self, dedupe="key"):
        self.ans, self.derived, self.overlay = {}, {}, True
        self.pending, self.complete, self.credit = [], {}, {}
        self.armed_by = {}          # intent ledger: arms per origin, independent of the sweep
        self.dedupe = dedupe
    def _arm(self, step, origin):
        self.pending.append((("complete", step), origin))
        self.armed_by[origin] = self.armed_by.get(origin, 0) + 1
    def commit(self, step, value, origin):
        i = STEPS.index(step)
        self.ans[step] = value
        for s in STEPS[i + 1:]:
            self.ans.pop(s, None); self.complete.pop(s, None)
        self._arm(step, origin)
        if step == "genre" and value in DEFAULT_TONE:
            self.ans["tone"] = DEFAULT_TONE[value]
            self._arm("tone", "auto")
        self._recompute()
    def force(self, answers):          # test-only hook: sets answers, nothing else
        self.ans = dict(answers)
    def _recompute(self):
        self.derived = {s: "%s:%s" % (s, self.ans[s]) for s in STEPS if s in self.ans}
        self.overlay = "ending" not in self.ans
    def sweep(self):
        seen = {}
        for key, origin in self.pending:
            if key not in seen: seen[key] = set()
            if self.dedupe == "key":
                if seen[key]: continue           # keep the first armer only
                seen[key].add(origin)
            else:                                # origin-set dedupe: one effect, all origins credited once
                if origin in seen[key]: continue
                seen[key].add(origin)
            if key[1] in self.ans:               # an effect for an invalidated step lands as a no-op
                self.complete[key[1]] = True
            self.credit[origin] = self.credit.get(origin, 0) + 1
        self.pending = []
    def view(self):
        return (tuple(sorted(self.ans.items())), tuple(sorted(self.derived.items())), self.overlay,
                tuple(sorted(self.complete.items())))

def rebuild(answers):
    """wizard lesson's oracle: replay the FINAL answers through commit() only"""
    w = Wizard()
    for s in STEPS:
        if s in answers:
            if w.ans.get(s) != answers[s]: w.commit(s, answers[s], "rebuild")
    w.sweep()
    return w

LOG = [(1, "genre", "noir", "player"), (2, "tone", "wry", "player"), (3, "ending", "open", "player")]

def real_play(log, dedupe="key"):
    w, t = Wizard(dedupe), None
    for tick, step, val, origin in log:
        if t is not None and tick != t: w.sweep()
        w.commit(step, val, origin); t = tick
    w.sweep()
    return w

def hook_single_sweep(log, dedupe="key"):
    w = Wizard(dedupe)
    for _, step, val, origin in log: w.commit(step, val, origin)
    w.sweep()
    return w

def hook_per_commit(log, dedupe="key"):
    w = Wizard(dedupe)
    for _, step, val, origin in log: w.commit(step, val, origin); w.sweep()
    return w

def credit(w): return (w.credit.get("player", 0), w.credit.get("auto", 0))

real = real_play(LOG)
final = dict(real.ans)
oracle = rebuild(final)
res = {}
print("S1 real play: view", real.view()[0], "credit player/auto", credit(real), "arms", real.armed_by)
res["S1"] = credit(real) == (3, 1)
f = Wizard(); f.force(final)
print("S2 force hook: view oracle match", f.view() == oracle.view())
res["S2"] = f.view() != oracle.view()
h = hook_single_sweep(LOG)
print("S3 delegating hook, one sweep: view oracle match", h.view() == oracle.view(), "| state==real", h.view() == real.view(),
      "| credit", credit(h), "vs real", credit(real))
res["S3"] = h.view() == oracle.view() and h.view() == real.view() and credit(h) == (2, 1)
hp = hook_per_commit(LOG)
print("S4 delegating hook, sweep per commit: credit", credit(hp), "view match", hp.view() == oracle.view())
res["S4"] = credit(hp) == credit(real)
hs = hook_single_sweep(LOG, "origins"); rs = real_play(LOG, "origins")
print("S5 origin-set dedupe: hook one sweep credit", credit(hs), "real", credit(rs))
res["S5"] = credit(hs) == credit(rs) == (3, 1)
print("S6 rebuild oracle credit", dict(oracle.credit), "vs real", dict(real.credit), "-> a credit check against the rebuild flags real play:",
      oracle.credit != real.credit)
res["S6"] = oracle.credit != real.credit
# S7: production itself coalesces: the player overrides tone on the SAME tick the genre autofill lands
LOG7 = [(1, "genre", "noir", "player"), (1, "tone", "wry", "player"), (2, "ending", "open", "player")]
r7 = real_play(LOG7); replay7 = real_play(LOG7)
print("S7 same-tick override in real play: credit", credit(r7), "| replay oracle", credit(replay7), "agrees with bug:",
      credit(r7) == credit(replay7), "| intent ledger arms", r7.armed_by)
intent_mismatch = r7.armed_by.get("player", 0) != r7.credit.get("player", 0)
res["S7"] = credit(r7) == (2, 1) and credit(r7) == credit(replay7) and intent_mismatch
# S8 control: backtrack via the hook (delegating, one sweep): genre changed after tone, invalidates tone
LOG8 = [(1, "genre", "noir", "player"), (2, "tone", "wry", "player"), (3, "genre", "comedy", "player"), (4, "ending", "open", "player")]
r8, h8 = real_play(LOG8), hook_single_sweep(LOG8)
o8 = rebuild(dict(r8.ans))
print("S8 backtrack: real credit", credit(r8), "hook credit", credit(h8), "hook view==oracle", h8.view() == o8.view())
res["S8_view"] = h8.view() == o8.view()
lost8 = (sum(r8.credit.values()) - sum(h8.credit.values()))
print("checks", res)
ok = all(res.values())
print("RESULT: %s delegating one-sweep hook passes full-view rebuild oracle (state==real) but credits player %d/auto %d vs real %d/%d; per-commit sweep %d/%d; origin-set %d/%d; rebuild has no origins (credit %s); same-tick real play loses too (%d/%d) and only intent ledger (player arms %d) sees it; backtrack hook loses %d credits"
      % ("PASS" if ok else "FAIL", *credit(h), *credit(real), *credit(hp), *credit(hs), dict(oracle.credit), *credit(r7), r7.armed_by["player"], lost8))
