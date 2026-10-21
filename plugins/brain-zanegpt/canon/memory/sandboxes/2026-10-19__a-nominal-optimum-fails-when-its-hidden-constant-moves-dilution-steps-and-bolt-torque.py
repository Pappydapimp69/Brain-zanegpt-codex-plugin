# Prediction (before run): both lessons hide a constant (pipette floor a, friction factor K).
# 1) Dilution 1000x, V=1000uL final per step, step error max(0.5%, a/transfer_uL), summed.
#    Nominal-best step count at a=0.5 is 3 (E1 prior: 3 at 0.5). Over a in [0.05, 2.0] the nominal pick's
#    worst-case error is larger than the minimax pick's, and the minimax pick is 4 steps.
# 2) Torque tuned to K=0.20 (target 100% proof) with true K in [0.12, 0.22]: worst overload is 167% of proof
#    (=0.20/0.12); the safe minimax torque (cap overload at 100% at K=0.12) leaves a worst underload of 55%.
#    So: no torque fits the whole range; a spec must name its K (nominal regret 67% vs minimax 45% gap).
def dil_err(n, a, V=1000.0, D=1000.0):
    f = D ** (1.0 / n); v = V / f
    return n * max(0.005, a / v)
A = [0.05, 0.1, 0.2, 0.5, 1.0, 1.5, 2.0]
nom = min(range(1, 13), key=lambda n: dil_err(n, 0.5))
worst = {n: max(dil_err(n, a) for a in A) for n in range(1, 13)}
mm = min(worst, key=worst.get)
print("nominal-best steps at a=0.5:", nom, "worst-case err", round(worst[nom]*100, 2), "%")
print("minimax steps:", mm, "worst-case err", round(worst[mm]*100, 2), "%")
for n in range(1, 13): print(" steps", n, "worst", round(worst[n]*100, 2), "%", " at a=0.5", round(dil_err(n, .5)*100, 2), "%")
Ks = [0.12, 0.14, 0.16, 0.18, 0.20, 0.22]
def load(T, K): return T / (K * 1.0)            # proof fraction with T in units where K=.20 gives 1.0 at T=0.2
def regret(T): return max(abs(load(T, K) - 1.0) for K in Ks)
Tn = 0.20
grid = [round(0.10 + 0.005 * i, 3) for i in range(0, 40)]
Tm = min(grid, key=regret)
print("nominal torque", Tn, "worst deviation", round(regret(Tn)*100), "% overload", round(load(Tn, .12)*100), "%")
print("minimax torque", Tm, "worst deviation", round(regret(Tm)*100), "%")
safe = 0.12  # no overload at K=.12
print("overload-safe torque", safe, "worst underload", round((1 - load(safe, .22))*100), "%")
ok = nom == 3 and mm != nom and worst[nom] > worst[mm] and round(load(Tn, .12), 2) == 1.67 and regret(Tm) < regret(Tn)
print("RESULT:", "PASS" if ok else "FAIL", f"dilution nominal {nom} steps worst {worst[nom]*100:.2f}% vs minimax {mm} steps {worst[mm]*100:.2f}%; torque nominal worst dev {regret(Tn)*100:.0f}% vs minimax {regret(Tm)*100:.0f}%")
