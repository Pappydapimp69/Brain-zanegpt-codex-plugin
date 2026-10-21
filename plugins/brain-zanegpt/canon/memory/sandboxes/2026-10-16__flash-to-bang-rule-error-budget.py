import math
# Flash-to-bang: distance = c(T) * seconds, c = 331.3*sqrt(1+T/273.15) m/s (ideal-gas speed of sound, dry air).
# Light travel time is ignored (3.3 us per km). Rules of thumb: km = s/3 ; miles = s/5.
def c(T): return 331.3 * math.sqrt(1 + T/273.15)
print("temp  c(m/s)  err(s/3 rule)  err(s/5 miles rule)")
worst3 = worst5 = 0
for T in (-10, 0, 10, 20, 30, 35):
    d_true_km = c(T) * 10 / 1000                    # true distance at a 10 s gap
    e3 = (10/3 - d_true_km) / d_true_km * 100
    e5 = (10/5 * 1.609344 - d_true_km) / d_true_km * 100
    worst3 = max(worst3, abs(e3)); worst5 = max(worst5, abs(e5))
    print("%4d  %6.1f  %+10.1f%%  %+10.1f%%" % (T, c(T), e3, e5))
# Timing error: a stopwatch/counting error of +/-0.5 s at the true distance, 20 C
for dist in (0.3, 1.0, 3.0, 10.0):
    s = dist*1000/c(20); err = 0.5 * c(20) / (dist*1000) * 100
    print("true %.1f km (gap %.1f s): +/-0.5 s count error = +/-%.0f%% of distance" % (dist, s, err))
close = 0.5*c(20)/300*100; far = 0.5*c(20)/10000*100
ok = worst3 < 5.0 and worst5 < 5.0 and close > 30 and far < 3
print("RESULT: %s rules stay within %.1f%% (s/3) and %.1f%% (s/5 miles) over -10..35 C; a 0.5 s count error is %.0f%% at 300 m but %.1f%% at 10 km" % ("PASS" if ok else "FAIL", worst3, worst5, close, far))
