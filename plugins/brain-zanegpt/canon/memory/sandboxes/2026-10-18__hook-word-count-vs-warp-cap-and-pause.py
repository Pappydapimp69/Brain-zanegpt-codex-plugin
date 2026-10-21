# Sandbox: hook caption of N words in a 3 s hook window, film-engine pace 5 words per 3 s.
# Prediction (before first run): needed warp = max(1, N/5); only N<=7 stays under the 1.5 cap (N=8 -> 1.6,
# N=9 -> 1.8, N=10 -> 2.0). A pause fixed at the 3 s mark misses the warped caption end by 3*(warp-1) s,
# which exceeds 0.5 s for N=6..10 (5 of 6 cases). BREAK: N=5 has warp 1.0 and lag 0.
WIN, PACE, CAP = 3.0, 5 / 3.0, 1.5     # seconds, words per second, warp cap
rows = {}
for n in (5, 6, 7, 8, 9, 10):
    need = n / PACE                    # reading seconds
    warp = max(1.0, need / WIN)
    end = WIN * warp                   # warped caption end
    lag = end - WIN                    # fixed-3s pause vs caption-end pause
    rows[n] = (warp, end, lag, warp <= CAP + 1e-9)
    print("N=%2d warp=%.2f caption_end=%.2fs fixed3s_lag=%.2fs under_cap=%s" % ((n,) + rows[n]))
under = [n for n, v in rows.items() if v[3]]
late = [n for n, v in rows.items() if v[2] > 0.5]
ok = (max(under) == 7 and late == [6, 7, 8, 9, 10] and rows[5][2] == 0.0)
print("RESULT: %s max hook words under the 1.5 cap = %d; fixed 3 s pause misses by >0.5 s for N=%s; N=5 lag 0"
      % ("PASS" if ok else "FAIL", max(under), late))
