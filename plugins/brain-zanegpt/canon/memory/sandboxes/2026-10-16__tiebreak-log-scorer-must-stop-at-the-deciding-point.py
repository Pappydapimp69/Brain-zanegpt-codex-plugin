"""Sandbox: scoring a recorded tennis tie-break log. Composes bowling-tenth-frame-scoring/E1 (score by the unit counter, a loop over the raw
record counts the fill balls) with tennis-tiebreak-server-rotation/E1 (check the SEQUENCE 0,1,1,0,0,1, not the counts).
Hidden assumption: the bowling trap (extra recorded items after the deciding unit) transfers to tie-breaks, where a log may carry trailing points
past the 7-point, 2-point-lead finish (practice rally recorded on, a doubled entry). Rule: first to 7 with a 2-point lead.
FIRST RUN FAILED (3/8 and 5/8) because I hand-typed several logs wrongly; fixtures are now built from the intended score and the prediction is unchanged.
PREDICTION (before run): on 8 logs, 3 of them with trailing points, the tally-everything scorer gets exactly 5/8 right and the stop-at-decision scorer 8/8;
the server-sequence check on the first six points accepts the true rotation and rejects both wrong ones in 8/8 logs, while a serve-COUNT check
at 12 points accepts all three rotations (so it cannot tell them apart); BREAK: a log of 6-6 then A, A (8-6) stays legal, and a log ending 7-6 is incomplete, not a win."""
def decide(points):            # unit-counter: stop at the deciding point
    a = b = 0
    for i, p in enumerate(points):
        a += p == "A"; b += p == "B"
        if max(a, b) >= 7 and abs(a - b) >= 2:
            return (a, b), i + 1
    return None, len(points)

def tally(points):             # roll-loop analogue: counts every recorded point
    a, b = points.count("A"), points.count("B")
    return (a, b) if max(a, b) >= 7 and abs(a - b) >= 2 else None

def build(a, b):               # a legal log ending exactly at a-b, A leading: alternate, then the winner's last points
    k = min(a, b)
    return "AB" * k + ("A" if a > b else "B") * abs(a - b)
LOGS = [  # (log, truth score or None); built from the intended final score, never typed by hand
 (build(7, 0), (7, 0)), (build(7, 5), (7, 5)), (build(8, 6), (8, 6)), (build(9, 7), (9, 7)),
 (build(7, 0) + "BB", (7, 0)),          # trailing points after the finish
 ("B" * 7 + "AAA", (0, 7)),             # trailing
 (build(8, 6) + "B", (8, 6)),           # trailing
 ("AB" * 6 + "A", None),                # 7-6: break case, incomplete not a win
]
def expect(log, truth):
    return decide(log)[0] == truth
ok_tally = ok_dec = 0
for log, truth in LOGS:
    t, d = tally(log), decide(log)[0]
    ok_tally += t == truth; ok_dec += d == truth
    print(log, "truth", truth, "tally", t, "decide", d)

def server(n, rule):           # 0 = first server
    return {"true": ((n + 1) // 2) % 2, "pairs": (n // 2) % 2, "alt": n % 2}[rule]
seq = {r: [server(n, r) for n in range(6)] for r in ("true", "pairs", "alt")}
cnt12 = {r: sum(server(n, r) for n in range(12)) for r in seq}
seq_ok = seq["true"] == [0, 1, 1, 0, 0, 1] and seq["pairs"] != seq["true"] and seq["alt"] != seq["true"]
cnt_same = len(set(cnt12.values())) == 1
print("sequences", seq, "serve counts at 12", cnt12)
ok = ok_tally == 5 and ok_dec == 8 and seq_ok and cnt_same
print("RESULT: %s tally-everything %d/8, stop-at-decision %d/8; sequence check separates 3 rotations, counts at 12 points all equal=%s" % (
    "PASS" if ok else "FAIL", ok_tally, ok_dec, cnt_same))
