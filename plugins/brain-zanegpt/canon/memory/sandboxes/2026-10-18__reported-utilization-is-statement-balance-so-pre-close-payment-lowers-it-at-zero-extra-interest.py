# Card model: limit 10000, 30-day cycle, 3000 spent evenly (100/day), statement closes at
# day 30, due 25 days later. Reported utilization = statement balance / limit.
# PREDICTION (before run): (A) pay in full only at the due date -> reported 30.0%;
# (B) pay 2900 on day 29 (before close) -> reported 1.0%; (C) BREAK: same 2900 paid on day 40
# (after close, before due) -> reported still 30.0%; interest is 0 in A, B, C (full balance
# paid by due date). (D) carrying a 3000 balance at 22.15% APR costs 55.38 in month 1 and
# the effective annual rate with monthly compounding is about 24.6%, above both the nominal
# 22.15% and the 10.47% S&P 500 average from the kernels.
LIMIT, DAILY, CYCLE, APR = 10000, 100, 30, 0.2215
SP500 = 0.1047
def cycle(pre_close_payment=0, post_close_payment=0, pay_due_in_full=True):
    bal = 0.0
    for day in range(1, CYCLE + 1):
        bal += DAILY
        if day == 29: bal -= pre_close_payment
    statement = bal                       # balance at close is what gets reported
    reported = 100 * statement / LIMIT
    bal -= post_close_payment             # payment between close and due date
    interest = 0.0 if bal <= 0 or (pay_due_in_full and pre_close_payment + post_close_payment >= 0) else bal * APR / 12
    if pay_due_in_full: bal = 0.0         # remainder cleared by the due date -> grace period, no interest
    return reported, interest
A = cycle()
B = cycle(pre_close_payment=2900)
C = cycle(post_close_payment=2900)
carry_month = 3000 * APR / 12
eff = (1 + APR / 12) ** 12 - 1
print("A", A, "B", B, "C", C, "carry month interest", round(carry_month, 2), "effective annual", round(eff, 4))
ok = (A == (30.0, 0.0) and B == (1.0, 0.0) and C == (30.0, 0.0)
      and abs(carry_month - 55.38) < 0.01 and 0.245 < eff < 0.247 and eff > APR > SP500)
print("RESULT: %s reported util A %.1f%% B %.1f%% C %.1f%%, interest %.0f/%.0f/%.0f, carry cost %.2f/month, effective APR %.1f%% vs S&P %.2f%%"
      % ("PASS" if ok else "FAIL", A[0], B[0], C[0], A[1], B[1], C[1], carry_month, 100 * eff, 100 * SP500))
