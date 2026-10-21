"""Blind rebuild of seven E49 (time-remap beat insert keeps cues in sync except
spanning clips). Own fixture: 25 visual cues and 25 audio cues in matched pairs
at times from a seeded LCG over 0-120 s; 4 continuous clips (start, duration).
Insert a beat of L = 2.5 s at T = 47.0 s. HAND EDIT model: an editor shifts
every cue at t >= T in the visual list, but in the audio list uses '>' instead
of '>=' (a boundary slip) and misses cues listed after a page break (index>=20),
deterministic, not random. REMAP: dispatcher plays every cue at f(t) = t + L if
t >= T else t; clips are scheduled by f(start) and played for their duration.
PREDICTION (before running): hand edit leaves >= 1 pair out of sync; remap 0;
a cue exactly at T fires once, at T + L; a clip spanning T ends exactly L early
relative to f(end); a clip ending before T unaffected; a clip starting at/after
T unaffected. Break scenario: if clips store their END time (not duration) and
the dispatcher also remaps the end, the spanning clip is stretched (plays L
longer than authored) instead of ending early - the 'ends early' finding
depends on duration-scheduled clips.
"""
import sys
print("python", sys.version.split()[0])
x = 99
def u():
    global x; x = (1103515245*x + 12345) & 0x7fffffff; return x/0x7fffffff
T, L = 47.0, 2.5
times = sorted(round(u()*120, 1) for _ in range(24)) + [T]; times.sort()
vis = list(times); aud = list(times)
f = lambda t: t + L if t >= T else t
hv = [t+L if t >= T else t for t in vis]
ha = [t+L if (t > T and i < 20) else t for i, t in enumerate(aud)]
hand_off = sum(abs(a-b) > 1e-9 for a, b in zip(hv, ha))
rv = [f(t) for t in vis]; ra = [f(t) for t in aud]
remap_off = sum(abs(a-b) > 1e-9 for a, b in zip(rv, ra))
atT = [f(t) for t in vis if t == T]
print("hand edits off:", hand_off, "of", len(vis), "| remap off:", remap_off, "| cue at T ->", atT)
clips = {"before": (10.0, 20.0), "spanning": (40.0, 15.0), "at_T": (47.0, 5.0), "after": (60.0, 8.0)}
res = {}
for k, (s, d) in clips.items():
    played_end = f(s) + d; intended_end = f(s+d) if (s+d) != T else s+d
    res[k] = round(intended_end - played_end, 6)
print("ends early by (duration-scheduled):", res)
# break: end-time-stored clips, both ends remapped
s, d = clips["spanning"]; stretched = (f(s+d) - f(s)) - d
print("break: end-remapped spanning clip plays longer than authored by", stretched)
ok = hand_off >= 1 and remap_off == 0 and atT == [T+L] and res["spanning"] == L \
     and res["before"] == 0 and res["after"] == 0 and res["at_T"] == 0
print(f"RESULT: {'PASS' if ok else 'FAIL'} hand off {hand_off}/{len(vis)}, remap 0; spanning clip ends {res['spanning']} s early; end-remapped clip stretched {stretched} s instead")
