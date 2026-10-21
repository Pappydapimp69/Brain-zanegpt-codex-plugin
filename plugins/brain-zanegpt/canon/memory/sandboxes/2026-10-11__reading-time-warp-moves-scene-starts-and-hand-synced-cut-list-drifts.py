"""Edge: film E2 (caption reading-time warp) + brain E132 (coverage cannot see
hand-synced sidecar drift). Hand-kept bar-grid cut list vs scene starts after
warp. Prediction (before first run): a presence/coverage check stays green for
all 8 scenes while at least 5 of 8 hand-kept cut times drift by one bar or
more after warp; deriving cuts from warped durations gives 0 drift; snapping
derived cuts to the bar grid costs under 1 bar per scene but cumulative
offset of authored length stays bounded. Assumed constants."""
BAR = 2.0
WORDS = [12, 40, 8, 55, 20, 33, 6, 48]            # caption words per scene
AUTH = [8.0, 8.0, 6.0, 10.0, 8.0, 8.0, 6.0, 10.0]  # authored seconds per scene
need = [1.0 + w / 2.6 for w in WORDS]               # E2 reading time, one caption per scene

def starts(durs):
    t, out = 0.0, []
    for d in durs:
        out.append(t); t += d
    return out

def warped(authored, wmax=None):
    out = []
    for a, n in zip(authored, need):
        f = max(1.0, n / a)
        if wmax: f = min(f, wmax)
        out.append(a * f)
    return out

W = warped(AUTH)
factors = [w / a for w, a in zip(W, AUTH)]
hand_cuts = starts(AUTH)                 # hand-synced once, before warp existed
real_starts = starts(W)
coverage = sum(1 for _ in hand_cuts) / len(WORDS)
drift = [abs(r - h) for r, h in zip(real_starts, hand_cuts)]
bars_drift = [d / BAR for d in drift]
n_drift = sum(1 for b in bars_drift if b >= 1.0)
print("1) per-scene warp:", [round(f, 2) for f in factors], "max", round(max(factors), 2))
print(f"2) coverage check (every scene has a cut): {coverage:.0%}; drifted >=1 bar: {n_drift}/8; worst {max(bars_drift):.1f} bars")

derived = starts(W)
d2 = sum(1 for r, c in zip(real_starts, derived) if abs(r - c) > 1e-9)
print(f"3) derive cuts from warped durations: drift count {d2}/8")

# snap each scene length UP to whole bars, then derive
snapped = [BAR * -(-d // BAR) for d in W]
snap_starts = starts(snapped)
extra = [s - w for s, w in zip(snapped, W)]
print(f"4) bar-snapped scene lengths: extra per scene max {max(extra):.2f}s (<{BAR}s), total film {sum(W):.1f}s -> {sum(snapped):.1f}s")

# break case: cap warp at 1.5 (E2 advice) -> reading time slack negative
capped = warped(AUTH, wmax=1.5)
short = [i for i, (c, n) in enumerate(zip(capped, need)) if c + 1e-9 < n]
print(f"5) warp capped at 1.5: scenes whose caption is under reading time: {short}")

ok = coverage == 1.0 and n_drift >= 5 and d2 == 0 and max(extra) < BAR and len(short) > 0
print(f"RESULT: {'PASS' if ok else 'FAIL'} coverage {coverage:.0%} green, drifted {n_drift}/8 (worst {max(bars_drift):.1f} bars), derived drift {d2}/8, snap extra max {max(extra):.2f}s, cap 1.5 leaves {len(short)} scenes short")
