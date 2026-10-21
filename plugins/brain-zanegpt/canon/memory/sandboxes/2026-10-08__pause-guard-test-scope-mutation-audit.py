# Wrapper chain: base update guarded by paused; later wrappers call predecessor then mutate own state.
FIELDS = ["time","bond","cooldown","heat","ascended"]
def make_game(mutant):
    s = {f:0 for f in FIELDS}; s["paused"]=False
    def base(s):
        if s["paused"]: return
        s["time"]+=1
    def wrap(field, prev, guarded):
        def u(s):
            prev(s)
            if guarded and s["paused"]: return
            s[field]+=1
        return u
    upd = base
    for f in FIELDS[1:]:
        upd = wrap(f, upd, guarded = (f != mutant))   # mutant = wrapper missing its own pause check
    return s, upd
def snapshot(s): return {f:s[f] for f in FIELDS}
def run_pause(mutant, watch):
    s, upd = make_game(mutant)
    for _ in range(3): upd(s)
    before = snapshot(s); s["paused"]=True
    for _ in range(5): upd(s)
    after = snapshot(s)
    return all(before[f]==after[f] for f in watch)     # True = test passes
suites = {
  "base-only (time)":        ["time"],
  "partial (time,bond)":     ["time","bond"],            # built to BREAK: lists only some fields
  "whole-state (all five)":  FIELDS,
}
MUTANTS = FIELDS[1:]
# sanity: unmutated game must pass every suite
assert all(run_pause(None, w) for w in suites.values())
res = {}
for name, watch in suites.items():
    killed = sum(1 for m in MUTANTS if not run_pause(m, watch))
    res[name] = len(MUTANTS)-killed
    print(f"{name}: survivors {res[name]}/{len(MUTANTS)}")
ok = res["base-only (time)"]==4 and res["partial (time,bond)"]==3 and res["whole-state (all five)"]==0
print(("RESULT: PASS" if ok else "RESULT: FAIL"),
  f"4 missing-pause-check mutants; survivors base-only={res['base-only (time)']} partial={res['partial (time,bond)']} whole-state={res['whole-state (all five)']}")
