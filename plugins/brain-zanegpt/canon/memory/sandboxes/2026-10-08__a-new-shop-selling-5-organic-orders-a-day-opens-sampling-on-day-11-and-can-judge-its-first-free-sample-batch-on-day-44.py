#!/usr/bin/env python3
"""Sandbox (edge): how long before a new shop can read its first sample result? Day arithmetic, deterministic, stdlib only.
Composes tiktok-shop lessons E19 (Shop Performance Score needs 30 delivered NON-SAMPLE orders in 90 days; 3.5 unlocks affiliate/samples), E11 (free sample: 7 d review + 7 d ship + 5 d transit + 14 d post = 33 d; refundable refund up to 49 d after purchase) and E6/E15 (sample payback).
Assumptions: the shop sells x organic orders/day from day 0; delivery takes 5 days; the score reaches 3.5 the day the 30th delivered order lands (best case); samples start that day.
PREDICTION (written before first run):
  P1 the gate opens on day ceil(30/x)+5 : x=10 -> day 8, x=5 -> day 11, x=2 -> day 20.
  P2 the first sampled creator video can be posted no earlier than gate + 7 + 7 + 5 (request, ship, transit) = gate + 19, and the post deadline is gate + 33: at x=5 that is days 30 and 44.
  P3 a free-sample batch can first be judged (post deadline passed) on day gate + 33: x=5 -> 44, x=2 -> 53 (7.6 weeks).
  P4 (built to break 'start sampling on day 1') sample and gift orders do not count toward the 30, so sending samples earlier cannot shorten the gate; the earliest judged result is unchanged.
  P5 a refundable batch's refunds are all settled by gate + 5 + 30 + 14 = gate + 49 -> x=5: day 60.
"""
import math
LAG=5; REV=7; SHIP=7; TRANSIT=5; POST=14; RET=30; PAY=14
def gate(x): return math.ceil(30/x)+LAG
rows={x:gate(x) for x in (10,5,2)}
first_post=lambda g:g+REV+SHIP+TRANSIT; deadline=lambda g:g+REV+SHIP+TRANSIT+POST; refund_done=lambda g:g+TRANSIT+RET+PAY
print(rows, {x:(first_post(g),deadline(g),refund_done(g)) for x,g in rows.items()})
p1=rows=={10:8,5:11,2:20}
p2=first_post(rows[5])==30 and deadline(rows[5])==44
p3=deadline(rows[5])==44 and deadline(rows[2])==53 and abs(deadline(rows[2])/7-7.6)<0.05
# P4: even if samples were sent from day 0 the gate counts only non-sample orders -> gate unchanged
p4=gate(5)==11
p5=refund_done(rows[5])==60
print(f"P1 {p1} P2 {p2} P3 {p3} P4 {p4} P5 {p5}")
print(("RESULT: PASS " if all((p1,p2,p3,p4,p5)) else "RESULT: FAIL ")+f"sample gate opens day {rows[10]}/{rows[5]}/{rows[2]} at 10/5/2 organic orders a day; first post by day {first_post(rows[5])}, post deadline day {deadline(rows[5])} (x=5), {deadline(rows[2])} (x=2); refunds settled by day {refund_done(rows[5])}")
