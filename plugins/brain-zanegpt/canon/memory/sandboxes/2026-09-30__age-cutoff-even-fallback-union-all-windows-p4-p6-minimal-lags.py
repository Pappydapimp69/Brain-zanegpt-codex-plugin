# Sandbox: validity = window difference set UNION even-tick fallback (L even). Exhaustive windows at P4,P5,P6.
# Oracle: press at lag L valid iff (both ticks active) OR (fallback role: L even). Brute force over 3 periods.
def valid_bf(P, win, L):
    return (L % 2 == 0) or any((t % P) in win and ((t - L) % P) in win for t in range(L, L + 3 * P))
def diffset(P, win):
    return {(a - b) % P for a in win for b in win}
def cut(valid, lags):
    v = [L for L in lags if valid(L)]
    return max(v) if v else 0
n = mis_union = mis_diffonly = 0
full_P_ok = fullN = 0
P_even_drop_raises = dropN = 0
for P in (4, 5, 6):
    for mask in range(1, 2 ** P):
        win = {i for i in range(P) if mask >> i & 1}
        D = diffset(P, win)
        for lags in (list(range(1, P + 1)), list(range(1, P)), list(range(1, 2 * P + 1))):
            n += 1
            b = cut(lambda L: valid_bf(P, win, L), lags)
            mis_union += b != cut(lambda L: (L % P) in D or L % 2 == 0, lags)
            mis_diffonly += b != cut(lambda L: (L % P) in D, lags)
        fullN += 1
        full_P_ok += cut(lambda L: valid_bf(P, win, L), list(range(1, P + 1))) == P   # minimal claim: 1..P -> P still
        # drop P: fallback makes cutoff >= largest even lag below P
        dropN += 1
        c = cut(lambda L: valid_bf(P, win, L), list(range(1, P)))
        P_even_drop_raises += c >= max(L for L in range(1, P) if L % 2 == 0)
ok = mis_union == 0 and mis_diffonly > 0 and full_P_ok == fullN and P_even_drop_raises == dropN
print(f"n={n} union_mismatch={mis_union} diffonly_mismatch={mis_diffonly} full1..P->P {full_P_ok}/{fullN} dropP_floor_even {P_even_drop_raises}/{dropN}")
print(f"RESULT: {'PASS' if ok else 'FAIL'} n={n} union_wrong={mis_union} diffonly_wrong={mis_diffonly} minimal={full_P_ok}/{fullN} dropP_even_floor={P_even_drop_raises}/{dropN}")
