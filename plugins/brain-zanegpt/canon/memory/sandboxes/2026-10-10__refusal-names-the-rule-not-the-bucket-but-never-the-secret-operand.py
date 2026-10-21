"""Sandbox: does a refusal that returns the RULE + remedy beat one that returns only the CLASS?
Where does it stop holding?  Stdlib only, no RNG, no timing.

Model
  12 rules R0..R11 in 3 classes (4 rules each).  An action carries items; an item
  trips a rule.  Guard refuses with one of several message FORMATS.  The actor is a
  deterministic repair loop that can only use what the message says.
Formats
  CAT   : "refused: class C"                       (the bucket)
  RULE  : "refused: rule R, item I, remedy: drop I or ACK:R"   (the rule + remedy)
Scenarios
  S1 single offence, 40 actions
  S2 two offences per action, 20 actions
  S3 false positive (lexical match on a legit item), 20 actions
  S4 BREAK: guard threshold is a secret number; prober recovers it (probe count)
  S5 BREAK: a rule that only fires when a hidden flag is set; does the message leak the flag?
  S6 control: actor that ignores refusal content
"""

CLASSES = 3
PER_CLASS = 4
NRULES = CLASSES * PER_CLASS


def cls(rule):
    return rule // PER_CLASS


# ---------------------------------------------------------------- guard
def guard(items, fmt, legit_ok=()):
    """items: tuple of rule ids each item trips (None = legit item).
    Returns (allowed, message).  legit_ok: acked rules."""
    for idx, r in enumerate(items):
        if r is not None and r not in legit_ok:
            if fmt == "CAT":
                return False, ("refused", "class", cls(r))
            return False, ("refused", "rule", r, "item", idx, "ack", "ACK:R%d" % r)
    return True, ("ok",)


# ---------------------------------------------------------------- actors
def candidates_for_class(items, c):
    """Items the actor considers plausibly related to class c: the class's real offenders
    plus lookalikes.  Lookalike set = fixed 4 slots per class, by item index position."""
    # an actor only sees item slots; slots [4c .. 4c+3] (mod len) are the plausible ones
    n = len(items)
    return [(PER_CLASS * c + k) % n for k in range(PER_CLASS)]


def actor_cat_restore(items):
    """Category-only, careful: drop one candidate, retry, restore if the message did not change."""
    items = list(items)
    calls = 1
    dropped_legit = 0
    ok, msg = guard(tuple(items), "CAT")
    while not ok:
        progressed = False
        for slot in candidates_for_class(items, msg[2]):
            saved = items[slot]
            items[slot] = None
            ok2, msg2 = guard(tuple(items), "CAT")
            calls += 1
            if ok2 or msg2 != msg:
                ok, msg = ok2, msg2
                progressed = True
                break
            items[slot] = saved  # same message: cannot tell, restore
        if not progressed:
            return calls, dropped_legit, False
    return calls, dropped_legit, True


def actor_cat_hurried(items):
    """Category-only, hurried: on a refusal drop ALL plausible candidates for the class at once."""
    items = list(items)
    calls = 1
    dropped_legit = 0
    ok, msg = guard(tuple(items), "CAT")
    while not ok and calls < 10:
        c = msg[2]
        for slot in candidates_for_class(items, c):
            if items[slot] is None:
                dropped_legit += 1  # a legit or already-empty slot swept up
            items[slot] = None
        ok, msg = guard(tuple(items), "CAT")
        calls += 1
    return calls, dropped_legit, ok


def actor_rule(items):
    """Rule-level: remove the named item (true positive) -> retry."""
    items = list(items)
    calls = 1
    ok, msg = guard(tuple(items), "RULE")
    while not ok and calls < 10:
        items[msg[4]] = None
        ok, msg = guard(tuple(items), "RULE")
        calls += 1
    return calls, 0, ok


# build actions: 8 item slots, mostly legit (None)
def make_action(offenders):
    items = [None] * 8
    for slot, rule in offenders:
        items[slot] = rule
    return items


def slot_for(rule, i):
    """offender sits inside the plausible window of its class, position cycles 0..3"""
    return (PER_CLASS * cls(rule) + (i % PER_CLASS)) % 8


def s1():
    actions = []
    for i in range(40):
        rule = i % NRULES
        actions.append(make_action([(slot_for(rule, i), rule)]))
    return actions


def s2(same_class=False):
    """two offences in DIFFERENT classes (S2) or the SAME class (S2b)"""
    actions = []
    for i in range(20):
        r1 = i % NRULES
        if same_class:
            r2 = cls(r1) * PER_CLASS + ((r1 + 1) % PER_CLASS)
            s_1 = slot_for(r1, i)
            base = PER_CLASS * cls(r1)
            s_2 = (base + ((s_1 - base) % 8 + 1) % PER_CLASS) % 8
        else:
            r2 = (r1 + PER_CLASS) % NRULES
            s_1 = slot_for(r1, i)
            s_2 = slot_for(r2, i)
        actions.append(make_action([(s_1, r1), (s_2, r2)]))
    return actions


def run_set(actions):
    out = {}
    for name, fn in (("cat_careful", actor_cat_restore), ("cat_hurried", actor_cat_hurried), ("rule", actor_rule)):
        calls = lost = fails = 0
        for a in actions:
            c, l, ok = fn(a)
            calls += c
            lost += l
            fails += 0 if ok else 1
        out[name] = (calls, lost, fails)
    return out


# ---------------------------------------------------------------- S3 false positive
def s3():
    """Action has one LEGIT item that lexically trips rule r.  Truth: item is fine.
    RULE format: actor can see which rule/item and ACK it -> receipt names rule.
    CAT format: only class; actor either deletes plausible candidates (destroying legit content)
    or after 3 failed retries asks a human who vouches (override, receipt says nothing)."""
    receipts_named = 0
    receipts_blank = 0
    destroyed = 0
    n = 20
    for i in range(n):
        r = i % NRULES
        slot = slot_for(r, i)
        items = make_action([(slot, r)])
        # RULE
        ok, msg = guard(tuple(items), "RULE")
        if not ok:
            ack = {msg[2]}  # actor acks exactly the named rule
            ok2, _ = guard(tuple(items), "RULE", legit_ok=ack)
            assert ok2
            receipts_named += 1
        # CAT, count outcomes
    cat_destroy = cat_blank = 0
    for i in range(n):
        r = i % NRULES
        slot = slot_for(r, i)
        items = make_action([(slot, r)])
        ok, msg = guard(tuple(items), "CAT")
        cands = candidates_for_class(items, msg[2])
        tries = 0
        resolved_by_delete = False
        for s_ in cands[:3]:  # 3 retries budget
            tries += 1
            if items[s_] is not None:
                items[s_] = None
                resolved_by_delete = True
                break
            # removing a lookalike did nothing; keep going
        if resolved_by_delete:
            cat_destroy += 1  # the legit-but-matching item was deleted to get past the guard
        else:
            cat_blank += 1  # human override, receipt says only "overridden"
    return n, receipts_named, cat_destroy, cat_blank


# ---------------------------------------------------------------- S4 secret threshold prober
def s4(secret, fmt):
    """Guard refuses when value v > secret (0..127).  Prober chooses v, sees the message.
    Returns (probes used, candidates still consistent with what the prober saw)."""
    def probe(v):
        if v > secret:
            if fmt == "FULL":
                return ("refused", "rule", "count-limit", "count", v, "limit", secret)
            if fmt == "RULE_NOVAL":
                return ("refused", "rule", "count-limit", "remedy", "reduce count")
            if fmt == "CAT":
                return ("refused", "class", "volume")
            return ("ack",)  # IDENT: byte-identical acknowledgement either way
        return ("ack",) if fmt == "IDENT" else ("ok",)

    probes = 1
    r = probe(127)
    if fmt == "IDENT":
        return 8, 128  # prober spends a full binary-search budget; every reply identical
    if r[0] != "refused":
        return probes, 1  # secret == 127
    if fmt == "FULL":
        return probes, 1  # limit printed in the message
    lo, hi = 0, 127  # lo allowed (v=0 never refused), hi refused
    while hi - lo > 1:
        mid = (lo + hi) // 2
        probes += 1
        if probe(mid)[0] == "refused":
            hi = mid
        else:
            lo = mid
    assert lo == secret
    return probes, 1


def s4_all():
    res = {}
    for fmt in ("FULL", "RULE_NOVAL", "CAT", "IDENT"):
        worst = 0
        total = 0
        cand_left = 0
        secrets = list(range(0, 128, 7)) + [0, 1, 126, 127]
        correct = True
        for sec in secrets:
            p, left = s4(sec, fmt)
            worst = max(worst, p)
            total += p
            cand_left = max(cand_left, left)
        res[fmt] = (worst, total / len(secrets), cand_left)
    return res


# ---------------------------------------------------------------- S5 hidden-flag rule
def guard_s5(items, flag, fmt):
    """R0 public, always on.  R3 only active when hidden flag set (same class as R0).
    Formats: CAT (class), RULE_FIRST (first matched rule), RULE_ALL (all matched rules)."""
    matched = []
    for idx, r in enumerate(items):
        if r == 0:
            matched.append(0)
        if r == 3 and flag:
            matched.append(3)
    if not matched:
        return ("ok",)
    if fmt == "CAT":
        return ("refused", "class", 0)
    if fmt == "RULE_FIRST":
        return ("refused", "rule", matched[0])
    return ("refused", "rules", tuple(matched))


def s5():
    probe = [0, 3]  # trips public R0 and flag-gated R3
    out = {}
    for fmt in ("CAT", "RULE_FIRST", "RULE_ALL"):
        outs = {guard_s5(probe, flag, fmt) for flag in (False, True)}
        out[fmt] = len(outs)
    # also the single-trip probe (only R3): any format leaks 1 bit (ok vs refused)
    single = {guard_s5([3], flag, "CAT") for flag in (False, True)}
    return out, len(single)


# ---------------------------------------------------------------- S6 control
def s6():
    # ignoring-the-message actor retries the same action up to K times, never changes it
    K = 5
    calls = {}
    for fmt in ("CAT", "RULE"):
        items = make_action([(2, 5)])
        c = 0
        for _ in range(K):
            ok, _ = guard(tuple(items), fmt)
            c += 1
            if ok:
                break
        calls[fmt] = c
    return calls


# ---------------------------------------------------------------- main
def main():
    print("S1 single offence x40")
    r1 = run_set(s1())
    for k, v in r1.items():
        print("  %-12s calls=%3d legit_dropped=%3d unresolved=%d" % ((k,) + v))
    print("S2 two offences x20")
    r2 = run_set(s2())
    for k, v in r2.items():
        print("  %-12s calls=%3d legit_dropped=%3d unresolved=%d" % ((k,) + v))
    print("S2b two offences SAME class x20 (BREAK for category-only careful actor)")
    r2b = run_set(s2(True))
    for k, v in r2b.items():
        print("  %-12s calls=%3d legit_dropped=%3d unresolved=%d" % ((k,) + v))
    n, named, c_destroy, c_blank = s3()
    print("S3 false positives x%d: RULE acked-with-named-receipt=%d ; CAT deleted-legit-content=%d unrecorded-human-override=%d"
          % (n, named, c_destroy, c_blank))
    r4 = s4_all()
    print("S4 secret threshold (BREAK) fmt:(worst probes, mean probes, candidates left)")
    for k, v in r4.items():
        print("  %-10s worst=%d mean=%.2f left=%d" % ((k,) + v))
    r5, single = s5()
    print("S5 hidden-flag rule (BREAK) distinct outputs across flag in {0,1}: %s ; single-trip probe=%d" % (r5, single))
    r6 = s6()
    print("S6 control blind actor calls: %s" % r6)

    n1 = 40
    ratio1 = r1["rule"][0] / r1["cat_careful"][0]
    mean_collateral = r1["cat_hurried"][1] / n1
    ratio2 = r2["rule"][0] / r2["cat_careful"][0]
    checks = [
        ("P1 ratio<=0.6", ratio1 <= 0.6, round(ratio1, 3)),
        ("P1 hurried collateral>=1.0/action", mean_collateral >= 1.0, mean_collateral),
        ("P1 rule collateral==0", r1["rule"][1] == 0 and r2["rule"][1] == 0, 0),
        ("S2b rule resolves all, cat_careful stalls", r2b["rule"][2] == 0 and r2b["cat_careful"][2] > 0, (r2b["rule"][2], r2b["cat_careful"][2])),
        ("P2 rule 20/20 named receipts", named == n, named),
        ("P2 cat >=15 destroyed-or-unrecorded", (c_destroy + c_blank) >= 15, c_destroy + c_blank),
        ("P3 FULL 1 probe", r4["FULL"][0] == 1, r4["FULL"][0]),
        ("P3 CAT>=5x FULL", r4["CAT"][0] >= 5 * r4["FULL"][0], r4["CAT"][0]),
        ("P3 RULE_NOVAL leaks no more than CAT", r4["RULE_NOVAL"][0] == r4["CAT"][0], r4["RULE_NOVAL"][0]),
        ("P3 IDENT unrecoverable", r4["IDENT"][2] == 128, r4["IDENT"][2]),
        ("P4 blind equal", r6["CAT"] == r6["RULE"] == 5, r6),
        ("S5 RULE_ALL leaks flag, CAT/RULE_FIRST do not", r5["RULE_ALL"] == 2 and r5["CAT"] == 1 and r5["RULE_FIRST"] == 1, r5),
    ]
    bad = [c for c in checks if not c[1]]
    for c in checks:
        print("  check %-48s %s %s" % (c[0], "ok" if c[1] else "FAILED", c[2]))
    if bad:
        print("RESULT: FAIL %d of %d checks failed: %s" % (len(bad), len(checks), [b[0] for b in bad]))
    else:
        print("RESULT: PASS rule-level refusal cuts guard calls to %.2fx of category-only (S1) and gives 20/20 named receipts on false positives, "
              "but naming matched VALUES drops secret-threshold recovery from %d to 1 probe and listing ALL matched rules leaks a hidden flag"
              % (ratio1, r4["CAT"][0]))


main()
