"""Sandbox (train edge): collective-reference E1 (two things that must agree
should be derived from one source, not hand-synced) composed with film E7
(insert a beat into a timeline-hard-coded film by remapping time at the
dispatcher: T minus the insert).
Model, exact: a film with 40 visual cues and 40 matching audio cues (same
times, must agree). Insert a beat of length L = 3.0 s at T = 30.0 s.
HAND: edit every cue after T in both lists; the human misses every 7th audio
  cue (a deterministic stand-in for a missed edit).
REMAP: lists untouched; the dispatcher plays a cue at story time t at wall time
  t if t < T, else t + L (the inserted beat occupies [T, T+L)).
Break case: continuous audio clips that START before T and are still playing at
T (spanning), played in wall time by the audio engine.
"""
L, T = 3.0, 30.0
CUES = [i * 1.5 for i in range(40)]           # 0.0 .. 58.5 s


def wall_remap(t):
    return t if t < T else t + L


def hand_lists():
    vis = [t + L if t >= T else t for t in CUES]
    aud = [t + L if t >= T and i % 7 != 0 else t for i, t in enumerate(CUES)]
    return vis, aud


def desync(vis, aud):
    return sum(abs(a - b) > 1e-9 for a, b in zip(vis, aud))


def main():
    hv, ha = hand_lists()
    hand = desync(hv, ha)
    rv = [wall_remap(t) for t in CUES]
    ra = [wall_remap(t) for t in CUES]
    remap = desync(rv, ra)
    boundary_ok = wall_remap(T) == T + L and wall_remap(T - 1e-6) < T
    # spanning clips: (start, length); audio engine plays them in wall time from wall_remap(start)
    clips = [(27.0, 6.0), (29.0, 4.0), (24.0, 2.0)]
    span_err = []
    for s, ln in clips:
        story_end = s + ln
        wall_end_engine = wall_remap(s) + ln                 # audio runs on, ignoring the insert
        wall_end_story = wall_remap(story_end) if story_end >= T else story_end
        span_err.append(round(wall_end_story - wall_end_engine, 6))
    print(f"hand edit: {hand} of {len(CUES)} cue pairs out of sync")
    print(f"dispatcher remap: {remap} out of sync; cue at T lands at {wall_remap(T)} (after the insert)")
    print(f"spanning clips (start, length) -> audio ends early by: " +
          ", ".join(f"{c}: {e:.1f}s" for c, e in zip(clips, span_err)))
    checks = [
        ("hand-syncing two lists leaves cues out of sync after one missed edit pattern", hand > 0),
        ("remapping at the dispatcher leaves 0 cue pairs out of sync", remap == 0),
        ("a cue exactly at T is placed after the insert, once (half-open boundary)", boundary_ok),
        ("break case: a clip spanning T ends exactly L early under remap", all(abs(e - L) < 1e-9 for e in span_err[:2])),
        ("a clip ending before T is unaffected", span_err[2] == 0),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; hand desync {hand}/40; "
          f"remap 0/40; spanning clips early by {span_err[0]:.1f}s and {span_err[1]:.1f}s; pre-T clip 0")


if __name__ == "__main__":
    main()
