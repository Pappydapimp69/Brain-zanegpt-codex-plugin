"""Loop 2 sandbox (phenomenology x art style). In real psychosis, 'minor
phenomena' (misperceiving a REAL object, a felt presence) are common and early;
a fully inserted phantom is the classic movie image. Which survives a player's
reality checks longer?
Exact, no RNG. Three hallucination forms:
  INSERTED   an object that is not there (SEVEN's PHANTOM_MARKER)
  ALTERED    a real object in the wrong state (a spent pylon that looks lit;
             SEVEN's FALSE_ANCHOR dead-pylons, seven E10's 'lie about state')
  PRESENCE   someone felt/seen at the edge, no object (DOUBLED_PARTY-like)
Verification verbs, each with a chance to expose each form:
  touch   INSERTED 1.0, ALTERED 0.0 (it is solid), PRESENCE 0.5 (you reach, nobody)
  ask     a companion who is not hallucinating: 0.8 for all three
  use     INSERTED 1.0, ALTERED 1.0 (it gives nothing back), PRESENCE 0.0 (nothing to use)
Player kits: SOLO-TOUCH (touch only), SOLO (touch+use), PARTY (touch+use+ask).
A player cycles through their verbs; expected number of checks until exposed
(capped at 12: 'never' if the per-cycle exposure is 0).
"""


def expected_checks(form, verbs, cap=12):
    p = {"touch": {"inserted": 1.0, "altered": 0.0, "presence": 0.5},
         "ask": {"inserted": 0.8, "altered": 0.8, "presence": 0.8},
         "use": {"inserted": 1.0, "altered": 1.0, "presence": 0.0}}
    alive, exp = 1.0, 0.0
    for i in range(cap):
        v = verbs[i % len(verbs)]
        hit = alive * p[v][form]
        exp += hit * (i + 1)
        alive -= hit
    return (exp + alive * (cap + 1)), alive


def main():
    kits = {"solo-touch": ["touch"], "solo": ["touch", "use"], "party": ["touch", "use", "ask"]}
    rows = {}
    for kit, verbs in kits.items():
        rows[kit] = {f: expected_checks(f, verbs) for f in ("inserted", "altered", "presence")}
        print(f"{kit:10s}: " + "  ".join(f"{f} {e:.2f} checks (survives {s:.2f})" for f, (e, s) in rows[kit].items()))
    checks = [
        ("an inserted phantom falls to the first touch in every kit", all(rows[k]["inserted"][0] == 1.0 for k in rows)),
        ("an altered real object survives touch-only checking entirely", rows["solo-touch"]["altered"][1] == 1.0),
        ("altered outlasts inserted in every kit", all(rows[k]["altered"][0] > rows[k]["inserted"][0] for k in rows)),
        ("break case: with a party to ask, every form is exposed within 3 checks on average",
         all(rows["party"][f][0] <= 3 for f in rows["party"])),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; solo-touch altered survives "
          f"{rows['solo-touch']['altered'][1]:.2f}; solo checks ins/alt/pres "
          + "/".join(f"{rows['solo'][f][0]:.2f}" for f in rows['solo']) + "; party "
          + "/".join(f"{rows['party'][f][0]:.2f}" for f in rows['party']))


if __name__ == "__main__":
    main()
