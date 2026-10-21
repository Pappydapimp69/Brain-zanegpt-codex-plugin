"""Sandbox: Sevin E1's false whistle (a third of quiet nights, bearing from a side hash
of (seed, day)) composed with Seven E23's cross-night bearing-consistency tell, read with
Seven E43's correct two-observation Bayes. Claim: the day-keyed false whistle hides a take
for ONE night only; two consecutive whistles from the same heard direction put P(someone
missing) >= 0.90, because a fresh random bearing per day can never be consistent like a
person who stays put. Stdlib only, fixed seeds, no wall time.

Predictions written before the first run:
 P1 S1 shipped: single whistle after a silent night -> P(missing) in [0.25, 0.45];
    two consecutive same-direction whistles -> P(missing) >= 0.90.
 P2 S2 per-run stable phantom spot: two-consistent P <= 0.60, BUT a whistle from outside
    the phantom's direction -> P >= 0.95 (a new leak).
 P3 S3 phantom EPISODES with the same statistics as a take: two-consistent P within 0.05
    of p/(p+q) and <= 0.60.
 P4 S4 (built to BREAK the claim): 4 heard directions and false rate 0.5 -> two-consistent
    P falls below 0.90 (claim has a boundary).
 P5 negative control: doubled-prior Bayes (E43's bug) on S1's exact two-night case lowers
    the posterior by more than 0.10.
"""
import random

SECTORS = 24
P_TAKE = 0.15        # per night, when nobody is missing (E23's prior)
NIGHTS = 14
RUNS = 30000

def side(seed, day, salt):
    # side stream keyed on (seed, day): never touches the run stream
    return random.Random(seed * 1_000_003 + day * 7919 + salt)

def heard(sector, dirs):
    return sector * dirs // SECTORS

def run(seed, mode, F, dirs, q=0.0):
    rng = random.Random(seed)                       # run stream
    missing_left = 0; real_sec = None
    ph_left = 0; ph_sec = None
    stable_ph = side(seed, 0, 99).randrange(SECTORS)
    obs = []  # per night: (heard dir or None, truly_missing)
    for day in range(1, NIGHTS + 1):
        # constant roll count: draw everything every night
        u_take = rng.random(); dur = rng.randint(2, 5); sec = rng.randrange(SECTORS)
        u_drift = rng.random(); step = rng.choice((-1, 1))
        if missing_left == 0 and u_take < P_TAKE:
            missing_left = dur; real_sec = sec
        elif missing_left > 0 and u_drift < 0.3:
            real_sec = (real_sec + step) % SECTORS
        s = side(seed, day, 1)
        u_f = s.random(); f_sec = s.randrange(SECTORS); f_dur = s.randint(2, 5)
        f_drift = s.random(); f_step = s.choice((-1, 1))
        if missing_left > 0:
            w = real_sec  # Sevin: the missing whistle at the wake every night
            truth = True
            missing_left -= 1
        else:
            truth = False
            w = None
            if mode == 'day':
                if u_f < F: w = f_sec
            elif mode == 'stable':
                if u_f < F: w = stable_ph
            elif mode == 'episode':
                if ph_left == 0 and u_f < q:
                    ph_left = f_dur; ph_sec = f_sec
                elif ph_left > 0 and f_drift < 0.3:
                    ph_sec = (ph_sec + f_step) % SECTORS
                if ph_left > 0:
                    w = ph_sec; ph_left -= 1
        obs.append((None if w is None else heard(w, dirs), truth))
    return obs, heard(stable_ph, dirs)

def measure(mode, F, dirs, q=0.0, seed0=0):
    single = [0, 0]; pair = [0, 0]; off = [0, 0]
    for r in range(RUNS):
        obs, ph = run(seed0 + r, mode, F, dirs, q)
        for t in range(1, NIGHTS):
            (a, _), (b, truth) = obs[t - 1], obs[t]
            if b is None: continue
            if a is None:
                single[0] += truth; single[1] += 1
            elif a == b:
                pair[0] += truth; pair[1] += 1
            if b != ph:
                off[0] += truth; off[1] += 1
    f = lambda x: x[0] / x[1] if x[1] else float('nan')
    return f(single), f(pair), f(off), pair[1]

def exact_two_night(F, dirs, real_consist, doubled=False):
    # Stationary-ish two-night slice: hypotheses missing-both, quiet-both, quiet-then-taken.
    p = P_TAKE; c0 = 1.0 / dirs
    hyps = [(p, 1.0 * (1/dirs) * real_consist, True),          # missing both nights
            ((1-p)*(1-p), F*F*(1/dirs)*c0, False),               # two false whistles
            ((1-p)*p, F*(1/dirs)*(1/dirs), True)]                # false then real take
    if doubled:  # E43's bug: (prior*L)^2 style, prior applied per observation
        w = [(pr*pr*L, t) for pr, L, t in hyps]
    else:
        w = [(pr*L, t) for pr, L, t in hyps]
    tot = sum(x for x, _ in w)
    return sum(x for x, t in w if t) / tot

results = []
s1 = measure('day', 1/3, 8)
print(f"S1 shipped (day-keyed, F=1/3, 8 dirs): single={s1[0]:.3f} pair={s1[1]:.3f} n_pair={s1[3]}")
results.append(('P1', 0.25 <= s1[0] <= 0.45 and s1[1] >= 0.90))

s2 = measure('stable', 1/3, 8)
print(f"S2 stable phantom spot: pair={s2[1]:.3f} off-phantom-direction={s2[2]:.3f}")
results.append(('P2', s2[1] <= 0.60 and s2[2] >= 0.95))

q = 0.15
s3 = measure('episode', 0, 8, q=q)
target = P_TAKE / (P_TAKE + q)
print(f"S3 phantom episodes q={q}: single={s3[0]:.3f} pair={s3[1]:.3f} target p/(p+q)={target:.3f}")
results.append(('P3', abs(s3[1] - target) <= 0.05 and s3[1] <= 0.60))

s4 = measure('day', 0.5, 4)
print(f"S4 BREAK (4 dirs, F=0.5): single={s4[0]:.3f} pair={s4[1]:.3f}")
results.append(('P4', s4[1] < 0.90))

rc = 0.85
ex = exact_two_night(1/3, 8, rc); exb = exact_two_night(1/3, 8, rc, doubled=True)
print(f"Exact two-night S1 slice: correct={ex:.3f} doubled-prior={exb:.3f}")
results.append(('P5', ex - exb > 0.10))

held = sum(ok for _, ok in results)
print("predictions:", ", ".join(f"{k}={'held' if ok else 'MISSED'}" for k, ok in results))
tag = "PASS" if held == len(results) else "FAIL"
print(f"RESULT: {tag} {held}/{len(results)} predictions held; S1 single {s1[0]:.3f} pair {s1[1]:.3f}; "
      f"stable pair {s2[1]:.3f} off-dir {s2[2]:.3f}; episodes pair {s3[1]:.3f} vs {target:.3f}; "
      f"break(4 dirs,F .5) pair {s4[1]:.3f}; exact {ex:.3f} vs doubled {exb:.3f}")
