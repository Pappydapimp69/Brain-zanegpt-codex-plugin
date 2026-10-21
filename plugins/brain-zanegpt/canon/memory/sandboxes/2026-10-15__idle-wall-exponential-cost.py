"""Sandbox: does cost = base * growth^n against production = rate * n produce a progress wall,
and does a prestige multiplier push it back? Deterministic, stdlib only.
Scenarios: 1) growth 1.07 (AdVenture Capitalist lemonade stand); 2) growth 1.00 (BREAK case: flat cost);
3) growth 1.07 with a x10 prestige multiplier."""
def wait_times(growth, mult=1.0, base=4.0, rate=1.0, n_buys=150):
    owned, money, t, waits = 1, 0.0, 0.0, []
    for _ in range(n_buys):
        cost = base * growth ** owned
        prod = rate * owned * mult
        dt = max(0.0, (cost - money) / prod)
        t += dt; money = money + prod * dt - cost; owned += 1
        waits.append(dt)
    return waits

w107 = wait_times(1.07); w100 = wait_times(1.00); wpre = wait_times(1.07, mult=10)
def first_over(ws, limit=60): return next((i for i, w in enumerate(ws) if w > limit), None)
print('growth 1.07: wait at buy 10/50/100/150 =', [round(w107[i], 2) for i in (9, 49, 99, 149)], 'first >60s at buy', first_over(w107))
print('growth 1.00: wait at buy 10/50/100/150 =', [round(w100[i], 3) for i in (9, 49, 99, 149)], 'first >60s at buy', first_over(w100))
print('1.07 + x10 prestige: first >60s at buy', first_over(wpre))
wall = first_over(w107) is not None and w107[-1] > 100 * w107[9]
flat = first_over(w100) is None and w100[-1] < w100[9]
pushed = first_over(wpre) is not None and first_over(wpre) > first_over(w107)
print(f"RESULT: {'PASS' if wall and flat and pushed else 'FAIL'} wall at buy {first_over(w107)} (1.07), none with flat cost, prestige x10 moves it to buy {first_over(wpre)}")
