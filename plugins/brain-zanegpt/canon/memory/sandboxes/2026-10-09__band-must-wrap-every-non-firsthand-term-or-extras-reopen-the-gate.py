#!/usr/bin/env python3
"""Sandbox: smallmouth#E1 banded hearsay vs august-10#E6 extras-outside-the-gate,
audited with smallmouth#E2's fires-at-least-once test. Deterministic, stdlib only,
no RNG, no timing."""

N = 8
TICKS = 168
GATE = -0.30          # confront threshold on total opinion
BAND = 0.25           # hearsay channel hard band, strictly inside the gate
HEAR_STEP = 0.05      # negative hearsay per retelling
PRICKLY = {4, 6}      # listeners with a personality bonus
FIRSTHAND_TICK = 100  # one genuine firsthand incident
FH_LISTENER, FH_SUBJECT = 1, 2

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def run(extra, mode):
    """mode: 'channel' = band clamps only the gossip channel, extras added after
    (august-10#E6 shape); 'wrap' = band clamps gossip+extras together."""
    gossip = {}
    first = {}
    done_conf = {}
    confs = []            # (tick, listener, subject, hearsay_only)
    max_chan = 0.0
    max_total = 0.0
    for t in range(TICKS):
        s, l, j = (t * 3) % N, (t * 5 + 1) % N, 2 + (t % 2) * 3   # subjects: 2 and 5
        if len({s, l, j}) == 3:
            k = (l, j)
            gossip[k] = clamp(gossip.get(k, 0.0) - HEAR_STEP, -BAND, BAND) if mode == "channel" else gossip.get(k, 0.0) - HEAR_STEP
        if t == FIRSTHAND_TICK:
            first[(FH_LISTENER, FH_SUBJECT)] = -0.35
        for (l2, j2), g in list(gossip.items()):
            ex = -extra if l2 in PRICKLY else 0.0
            if mode == "channel":
                hear = g
                total = g + ex + first.get((l2, j2), 0.0)
            else:
                hear = clamp(g + ex, -BAND, BAND)
                total = hear + first.get((l2, j2), 0.0)
            max_chan = max(max_chan, abs(g if mode == "channel" else hear))
            max_total = max(max_total, abs(total - first.get((l2, j2), 0.0)))  # hearsay-side total only
            if total <= GATE and t - done_conf.get((l2, j2), -99) > 24:
                hearsay_only = first.get((l2, j2), 0.0) == 0.0
                confs.append((t, l2, j2, hearsay_only))
                done_conf[(l2, j2)] = t
                gossip[(l2, j2)] = 0.0       # discharge (smallmouth#E1)
                first[(l2, j2)] = 0.0
        # firsthand edge with no gossip entry yet
        k = (FH_LISTENER, FH_SUBJECT)
        if k not in gossip and first.get(k, 0.0) <= GATE and t - done_conf.get(k, -99) > 24:
            confs.append((t, k[0], k[1], False)); done_conf[k] = t; first[k] = 0.0
    return confs, max_chan, max_total

def summarize(name, extra, mode):
    confs, mc, mt = run(extra, mode)
    ho = sum(1 for c in confs if c[3])
    fh = sum(1 for c in confs if not c[3])
    fires = len(confs) >= 1                 # smallmouth#E2 audit
    provenance_ok = ho == 0                 # smallmouth#E1 audit
    print(f"{name}: extra={extra} mode={mode} confrontations={len(confs)} "
          f"hearsay_only={ho} firsthand={fh} max_channel={mc:.2f} max_total={mt:.2f} "
          f"fires_audit={'ok' if fires else 'FAIL'} provenance_audit={'ok' if provenance_ok else 'FAIL'}")
    return ho, fh, mc, mt, fires, provenance_ok

s1 = summarize("S1 band-only", 0.0, "channel")
s2 = summarize("S2 extras-outside-band", 0.10, "channel")
s3 = summarize("S3 small-extras(break)", 0.04, "channel")
s4 = summarize("S4 band-wraps-all", 0.10, "wrap")

ok = (s1[0] == 0 and s1[3] <= 0.25 + 1e-9
      and s2[0] >= 2 and s2[3] >= 0.30 - 1e-9
      and s3[0] == 0 and s3[3] < 0.30
      and s4[0] == 0 and s4[3] <= 0.25 + 1e-9
      and all(s[4] for s in (s1, s2, s3, s4))          # fires audit passes everywhere
      and (not s2[5]) and s1[5] and s3[5] and s4[5])   # only provenance audit catches S2
if ok:
    print(f"RESULT: PASS band alone gives 0 hearsay-only confrontations, extras outside the band give {s2[0]} (max total {s2[3]:.2f} vs gate 0.30) while the fires-at-least-once audit passes in all 4 runs; extras within slack stay 0; wrapping band over hearsay+extras restores 0")
else:
    print(f"RESULT: FAIL prediction not reproduced s1={s1} s2={s2} s3={s3} s4={s4}")
