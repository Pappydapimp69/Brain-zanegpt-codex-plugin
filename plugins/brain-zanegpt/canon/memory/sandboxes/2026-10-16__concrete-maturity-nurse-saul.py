# Sandbox: Nurse-Saul maturity M = sum((T - T0) * dt) for T > T0 (datum T0 = -10 C, the usual ASTM C1074 default).
# Rule under test: two pours with equal maturity are at the same strength stage, so the time to reach a target
# maturity can be predicted for any temperature history; freezing below the datum adds nothing.
T0=-10.0
def maturity(temps_per_hour): return sum(max(0.0,T-T0) for T in temps_per_hour)
TARGET=maturity([20.0]*72)            # 3 days at 20 C is the reference stage
def hours_to_target(profile):
    m=0.0;h=0
    while m<TARGET and h<10000:
        m+=max(0.0,profile(h)-T0);h+=1
    return h
const=lambda T:(lambda h:T)
diurnal=lambda h:10+8*(1 if (h%24)<12 else -1)    # 18 C days, 2 C nights, mean 10 C
cold_snap=lambda h:-20.0 if (h%24)<12 else 5.0   # nights below the datum add nothing
r={}
for name,p in(("20C const",const(20)),("10C const",const(10)),("diurnal 18/2",diurnal),("5C const",const(5)),("cold snap -20/5",cold_snap)):
    r[name]=hours_to_target(p);print("%-16s %5d h to the 3-day-at-20C stage"%(name,r[name]))
# prediction: mean-temperature shortcut works when the profile stays above the datum, and fails when it dips below it
mean_cold=sum(cold_snap(h) for h in range(24))/24
naive_cold=hours_to_target(const(mean_cold))
print("cold snap mean %.1f C: constant-mean time %s h vs true %d h"%(mean_cold,naive_cold if naive_cold<10000 else "never",r["cold snap -20/5"]))
ok = r["20C const"]==72 and abs(r["diurnal 18/2"]-r["10C const"])<=12 and naive_cold>2*r["cold snap -20/5"]
print("RESULT: %s 72h at 20C; 10C const %d h is within 12 h of diurnal mean-10C %d h; cold snap true %d h vs constant-mean %s h"%("PASS" if ok else "FAIL",r["10C const"],r["diurnal 18/2"],r["cold snap -20/5"],naive_cold if naive_cold<10000 else "never"))
