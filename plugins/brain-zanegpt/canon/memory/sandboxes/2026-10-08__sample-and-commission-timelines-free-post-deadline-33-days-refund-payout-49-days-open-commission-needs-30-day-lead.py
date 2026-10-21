#!/usr/bin/env python3
"""Sandbox: day arithmetic for sample windows and commission-change lag. Deterministic, stdlib only.
Source windows (Seller University, read live 2026-10-08): free-sample request review <=7 d, ship <=7 d after approval, creator posts <=14 d after delivery;
refundable sample must meet criteria within 90 d else becomes a purchase; sales count after the return period (typically 30 d after delivery); refund takes 5-10 business days;
commission edits take effect 30 d (Open) / 5 d (Target) after the edit. ASSUMED transit 5 d, 10 business days = 14 calendar days.
PREDICTION (written before first run):
  P1 latest free-sample post deadline = 7+7+5+14 = 33 days after the request (33).
  P2 a refundable-sample refund that hits on the first possible day is paid at the latest 5+30+14 = 49 days after purchase (49), and the 90-day window leaves 41 days of slack beyond that (41).
  P3 a seller who raises the OPEN commission on day 0 for a launch on day 10 has the old rate for the whole launch (active rate on day 10 = old); the TARGET rate is live on day 5.
  P4 (built to break 'plan commission a week ahead') to have the Open rate live by launch day L, the edit must be made on or before L-30; a 14-day lead is too short for any L<30.
"""
T=5;REV=7;SHIP=7;POST=14;RET=30;PAY=14;WIN=90
p1=REV+SHIP+T+POST
refund_latest=T+RET+PAY; slack=WIN-refund_latest
def active(edit_day,effective_lag,day): return "new" if day>=edit_day+effective_lag else "old"
open10=active(0,30,10); tgt5=active(0,5,5); open29=active(0,30,29); open30=active(0,30,30)
lead14_ok=[L for L in range(0,60) if active(L-14,30,L)=="new"]
print(f"free post deadline {p1} d; refund latest {refund_latest} d, slack in 90 d window {slack} d; open@day10 {open10}, target@day5 {tgt5}, open@29 {open29}, open@30 {open30}; launch days reachable with a 14-day lead: {len(lead14_ok)}")
q1=p1==33; q2=refund_latest==49 and slack==41; q3=open10=="old" and tgt5=="new"; q4=open29=="old" and open30=="new" and len(lead14_ok)==0
print(f"P1 {q1} P2 {q2} P3 {q3} P4 {q4}")
print(("RESULT: PASS " if all((q1,q2,q3,q4)) else "RESULT: FAIL ")+f"free post deadline {p1} d after request; refund payout worst case {refund_latest} d after purchase; Open commission needs a {30}-day lead, Target {5}")
