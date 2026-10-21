# Rebuild of sandbox-sentinel-and-failfast-coverage-sweep#E1 with an independent fixture.
# Claim: a coverage sweep needs separate counters (winners, no-winner, errors) and must not
# abort on the first divergence; naive coercion inflates distinct, fail-fast truncates.

class Divergent(Exception):
    pass

def make_cases(n, none_at, err_at, opts=5):
    cases = []
    for i in range(n):
        if i in none_at:
            cases.append([0] * opts)
        elif i in err_at:
            cases.append("DIVERGE")
        else:
            # deterministic scores; winner index cycles through only 3 of 5 options
            w = (i * 2) % 3
            cases.append([(j + 1) * (5 if j == w else 1) % 7 if j != w else 50 for j in range(opts)])
    return cases

def winner(scores):
    if scores == "DIVERGE":
        raise Divergent("case diverged")
    m = max(scores)
    return None if m <= 0 else scores.index(m)

def naive_failfast(cases, coerce=lambda w: w):
    seen, s = 0, set()
    for c in cases:
        seen += 1
        s.add(coerce(winner(c)))  # raises -> sweep aborts
    return seen, s

def run_failfast(cases, coerce=lambda w: w):
    seen, s = 0, set()
    try:
        for c in cases:
            seen += 1
            s.add(coerce(winner(c)))
    except Divergent:
        pass
    return seen, s

def naive_continue(cases, coerce=lambda w: w):
    s = set(); seen = 0
    for c in cases:
        try:
            s.add(coerce(winner(c))); seen += 1
        except Divergent:
            continue
    return seen, s

def guarded(cases):
    winners, no_win, errs = set(), 0, 0
    for c in cases:
        try:
            w = winner(c)
        except Divergent:
            errs += 1; continue
        if w is None:
            no_win += 1
        else:
            winners.add(w)
    return winners, no_win, errs

def truth(cases):
    return {winner(c) for c in cases if c != "DIVERGE" and winner(c) is not None}

ok = True
def check(name, cond, detail):
    global ok
    ok &= bool(cond)
    print(("ok   " if cond else "FAIL ") + name + ": " + detail)

N = 15
cases = make_cases(N, none_at={2, 8, 13}, err_at={6})
T = truth(cases)
gw, gn, ge = guarded(cases)
check("guarded accounts every case", len(gw) == len(T) and gn == 3 and ge == 1
      and sum(1 for c in cases if c != "DIVERGE" and winner(c) is not None) + gn + ge == N,
      f"distinct={len(gw)} true={len(T)} no_winner={gn} errors={ge}")
seen, s = naive_continue(cases)
check("naive continue inflates by phantom None", len(s) == len(T) + 1 and None in s,
      f"naive distinct={len(s)} vs true {len(T)}")
fseen, fs = run_failfast(cases)
check("fail-fast truncates at divergence", fseen == 7 and fseen < N,
      f"fail-fast saw {fseen}/{N} (aborted at index 6)")

# Break 1: no-winner-free world -> naive continue is NOT inflated (coercion inflates only if a sentinel exists)
c2 = make_cases(N, none_at=set(), err_at={6})
_, s2 = naive_continue(c2)
check("no-sentinel world: naive == true", len(s2) == len(truth(c2)), f"{len(s2)} == {len(truth(c2))}")

# Break 2: sentinel coerced to int 0 collides with a real winner -> distinct NOT inflated,
# yet 3 no-winner cases are silently booked as winner 0. Count is right, meaning is wrong.
_, s3 = naive_continue(cases, coerce=lambda w: 0 if w is None else w)
check("colliding coercion hides inflation", len(s3) == len(T) and 0 in T,
      f"naive distinct={len(s3)} == true {len(T)} while 3 no-winner cases vanished")
# guarded still separates them under the same fixture
check("guarded still exposes them", gn == 3, f"no_winner={gn}")

# Break 3: divergence at the last case -> fail-fast loses no successful cases
c4 = make_cases(N, none_at={2, 8, 13}, err_at={N - 1})
f4, _ = run_failfast(c4)
check("late divergence: fail-fast saw all", f4 == N, f"saw {f4}/{N}")

# Break 4: divergence at first case -> fail-fast reports an empty sweep
c5 = make_cases(N, none_at={2, 8, 13}, err_at={0})
f5, fs5 = run_failfast(c5)
check("early divergence: fail-fast empty", f5 == 1 and len(fs5) == 0, f"saw {f5}/{N}, distinct={len(fs5)}")

print("RESULT: %s guarded sweep accounts 15/15 (distinct=%d no_winner=3 errors=1); naive continuing reads %d vs true %d; fail-fast saw 7/15; inflation is +1 only when a sentinel exists AND coerces to a non-colliding value (int-0 coercion reads %d==true while hiding 3 no-winner cases); truncation cost depends on error position (last: 15/15, first: 1/15)"
      % ("PASS" if ok else "FAIL", len(gw), len(s), len(T), len(s3)))
