# Prediction (before run): a cut list hand-copied for 120 BPM is on-beat for the 120 BPM variant and for any tempo whose beat
# grid shares its cut times (only some cuts), off-beat for most cuts at 128/140 BPM; derived-from-music cuts are 100% on-beat.
# With a 0.23 score loss prorated by off-beat share (the clock-recut loss from the ranking lesson), the hand list flips the winner.
TOL = 1/30           # one frame at 30 fps
CUT_BEATS = [4, 8, 12, 16, 20, 24, 28, 32, 36, 40]   # cut every 4 beats from beat 4
def beat_time(bpm, b): return b * 60.0 / bpm
hand = [beat_time(120, b) for b in CUT_BEATS]           # written once, for the 120 BPM draft, kept by hand
def derived(bpm): return [beat_time(bpm, b) for b in CUT_BEATS]
def on_beat_share(cuts, bpm):
    spb = 60.0 / bpm
    return sum(1 for t in cuts if min(t % spb, spb - t % spb) <= TOL) / len(cuts)
# variants: (name, bpm, base IPM x D1 score)
V = [("A", 120, 100.0), ("B", 128, 104.0), ("C", 140, 110.0)]
def score(base, share): return base * (1 - 0.23 * (1 - share))
rows = {}
for mode in ("hand", "derived"):
    out = []
    for n, bpm, base in V:
        cuts = hand if mode == "hand" else derived(bpm)
        s = on_beat_share(cuts, bpm); out.append((n, bpm, round(s, 2), round(score(base, s), 2)))
    rows[mode] = out; print(mode, out)
win = {m: max(rows[m], key=lambda r: r[3])[0] for m in rows}
# BREAK: tempo where hand list still lands on beat (multiple of 120 grid): 240 BPM beats are half-length so every cut stays on-beat.
brk = on_beat_share(hand, 240)
print("BREAK 240 BPM hand-list on-beat share", brk, "| winners", win)
ok = all(r[2] == 1.0 for r in rows["derived"]) and rows["hand"][1][2] < 0.5 and win["derived"] == "C" and win["hand"] != "C" and brk == 1.0
print(f"RESULT: {'PASS' if ok else 'FAIL'} hand list on-beat share {[r[2] for r in rows['hand']]} vs derived {[r[2] for r in rows['derived']]}; winner hand={win['hand']} derived={win['derived']}; 240 BPM share {brk}")
