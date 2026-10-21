"""Sandbox composing collective-reference/E1 (derive a map from the real artifact, a hand-kept sidecar drifts),
rank-ipm-times-d1-needs-fidelity-retention-link/E1 (rank recuts on IPM x D1) and
hook-frame0-audio-vs-promise-cap-recut-rank/E1 (gate every recut on a frame-0 audio hit before ranking).
Model (same shapes as the hook sandbox): nine recuts promise 0.2..1.0, delivery 0.5,
IPM = 10*(0.5+p)*(0.4 if first second silent else 1), D1 = 0.40*(1-1.5*max(0,p-0.5)).
Each recut file has a first-second RMS (silent if < 0.01). The GATE finds silent recuts and re-renders them with a
hit (restores the x1.0 IPM factor) BEFORE ranking. Three gates: none; SIDECAR (a list of silent recut ids written
when the batch was first cut, then the batch was re-rendered so ids shifted by one slot); DERIVED (reads RMS now).
PREDICTION (before run): (1) with no gate IPM x D1 picks 0.5 whenever the 0.5 recut is not silent (as the hook sandbox
found) but picks a wrong promise when ONLY the 0.5 recut is silent; (2) DERIVED returns 0.5 in all scenarios;
(3) SIDECAR returns 0.5 in the scenarios where it happens to cover the silent set and fails in at least one;
BREAK: silence only on the 0.5 recut with a sidecar shifted by one, where the sidecar fixes the wrong recut."""
P = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
D = 0.5
def ipm(p, silent): return 10.0 * (0.5 + p) * (0.4 if silent else 1.0)
def d1(p): return 0.40 * (1 - 1.5 * max(0.0, p - D))
def pick(silent, key): return max(P, key=lambda p: key(p, p in silent))
def rank_ipmd1(silent): return pick(silent, lambda p, s: ipm(p, s) * d1(p))
def rank_ipm(silent): return pick(silent, lambda p, s: ipm(p, s))
# true silent sets (what the audio files really are NOW)
SCEN = {"A none silent": set(), "B all silent": set(P), "C only p>=0.7 silent": {0.7, 0.8, 0.9, 1.0},
        "D BREAK only the delivery-matched 0.5 silent": {0.5}, "E only 0.4 silent": {0.4}, "F 0.5 and 0.6 silent": {0.5, 0.6}}
def shift(ids, k=1):  # sidecar recorded before re-render: slot i now holds what slot i-k held
    ix = {p: i for i, p in enumerate(P)}
    return {P[min(len(P) - 1, ix[p] + k)] for p in ids}
def gated(true_silent, gate):
    if gate == "none": left = true_silent
    elif gate == "derived": left = set()                        # reads RMS now: finds every silent recut, re-renders it
    else:                                                        # sidecar: re-renders the ids it remembers (stale by one slot)
        remembered = shift(true_silent)
        left = {p for p in true_silent if p not in remembered}
    return left
rows = {}
for name, ts in SCEN.items():
    r = {g: rank_ipmd1(gated(ts, g)) for g in ("none", "sidecar", "derived")}
    a = {g: rank_ipm(gated(ts, g)) for g in ("none", "sidecar", "derived")}
    rows[name] = (r, a)
    print(f"{name}: IPM*D1 picks {r}   IPM-alone picks {a}")
none_bad = [n for n, (r, a) in rows.items() if r["none"] != 0.5]
side_bad = [n for n, (r, a) in rows.items() if r["sidecar"] != 0.5]
der_bad = [n for n, (r, a) in rows.items() if r["derived"] != 0.5]
ok = (not der_bad and "D BREAK only the delivery-matched 0.5 silent" in none_bad and len(side_bad) >= 1
      and all(n.startswith(("A", "B", "C", "E")) for n in none_bad if n not in ("D BREAK only the delivery-matched 0.5 silent", "F 0.5 and 0.6 silent")))
print("wrong IPM*D1 pick -> no gate:", none_bad, " sidecar:", side_bad, " derived:", der_bad)
print("RESULT: %s IPM*D1 with no gate misses 0.5 in %d of %d scenarios (%s); stale sidecar misses in %d; gate derived from the audio misses in %d"
      % ("PASS" if ok else "FAIL", len(none_bad), len(SCEN), "; ".join(n[0] for n in none_bad), len(side_bad), len(der_bad)))
