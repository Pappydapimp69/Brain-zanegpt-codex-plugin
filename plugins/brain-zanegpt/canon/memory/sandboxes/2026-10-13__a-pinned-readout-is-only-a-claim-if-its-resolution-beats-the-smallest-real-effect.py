"""A pinned-at-zero readout beside a moving clock: when does 'still' mean 'nothing is happening'?
Deterministic. Decay index = rate_per_year * years (0..1 scale). Panel shows the index to `dec` decimals and a
bar BAR_PX wide (rounded to whole pixels). Viewer concludes 'nothing decomposing' iff the readout AND bar equal their
t=0 values at every sampled time. Truth: nothing decomposes iff rate == 0.
Also compares the adaptive line gated on the proxy (displayed value == 0) vs the asserted predicate (true rate == 0)."""
YEARS = [0, 1, 10, 43]          # clock keeps rolling (the 'something else moves' companion)
BAR_PX = 200
RATES = [0.0, 0.0002, 0.002, 0.02]   # per year

def panel(rate, y, dec, bar=True):
    v = rate * y
    return (round(v, dec), round(v * BAR_PX) if bar else 0)

def viewer_says_still(rate, dec, companion=True, bar=True):
    if not companion:      # nothing else moves: viewer cannot tell 'still' from 'ignored/frozen UI'
        return False
    first = panel(rate, YEARS[0], dec, bar)
    return all(panel(rate, y, dec, bar) == first for y in YEARS)

lies = {}
for dec in (0, 1, 2, 3, 4):
    row = []
    for r in RATES:
        says = viewer_says_still(r, dec, True, False)
        truth = (r == 0.0)
        row.append((r, says, truth))
    lies[dec] = [r for r, s, t in row if s and not t]       # false 'nothing happening'
    print(f"number only dec={dec}: false-still rates {lies[dec]}  true-still detected {[r for r,s,t in row if s and t]}")

print("no companion clock: still detected as claim for rate 0 ->", viewer_says_still(0.0, 3, companion=False))
# adaptive copy: proxy = displayed value equals 0 ; predicate = true rate == 0
for dec in (1, 3):
    proxy_wrong = [r for r in RATES if (panel(r, YEARS[-1], dec)[0] == 0) != (r == 0.0)]
    print(f"dec={dec}: copy gated on displayed zero says wrong thing for rates {proxy_wrong}")
bar_lies = [r for r in RATES if viewer_says_still(r, 0, True, True) and r != 0.0]
print("with a 200px bar and dec=0, false-still rates:", bar_lies)
# BREAK: tiny effect below pixel AND decimal resolution at long horizon still passes as 'still'
tiny = 0.000001
print("BREAK rate 1e-6 at dec=3 reads still:", viewer_says_still(tiny, 3), "| with dec=7:", viewer_says_still(tiny, 7))
ok = bool(lies[0]) and bool(lies[1]) and not lies[2] and not lies[3] and not bar_lies and viewer_says_still(tiny, 3) and not viewer_says_still(0.0, 3, False) and viewer_says_still(0.0, 3)
print(("RESULT: PASS" if ok else "RESULT: FAIL") + f" false-still rates by decimals { {d: l for d, l in lies.items()} }")
