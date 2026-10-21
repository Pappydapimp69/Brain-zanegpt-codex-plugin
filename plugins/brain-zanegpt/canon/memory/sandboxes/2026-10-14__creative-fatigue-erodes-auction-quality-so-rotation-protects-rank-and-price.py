"""Composes a quality-weighted second-price auction (rank = bid*quality, price = rival rank / own quality
+ 0.01, rank floor 1.0, my assumed rule as in sandbox-quality-weighted-auction/E1) with per-exposure creative
fatigue (quality = q0 * decay**exposures-per-person-to-that-creative, as in brainwork/E69). Exposures only
accrue in weeks the ad actually serves. 12 weeks, 3 impressions per person per week, 1000 people.
Deterministic, stdlib only.

PREDICTION (before first run), decay 0.85, q0 2.5, rival rank 1.2:
 P1 single creative, bid 1.0 drops out of the auction at week 2 (rank below the floor) and has the fewest clicks.
 P2 single creative, doubled bid 2.0 serves 3 weeks, so doubling the bid buys 1 extra week of serving, not 12.
 P3 rotating 6 creatives at bid 1.0 beats doubled bid on total clicks by >= 3x and has the lowest cost per click.
 P4 BREAK: at decay 0.99 the three strategies are within 10% of each other on clicks (the rotation advantage needs steep fatigue).
 P5 once a single creative is below the floor it never returns (no recovery), so clicks after drop-out are 0.
"""
WEEKS, PEOPLE, IMPS = 12, 1000, 3
def campaign(decay, bid, k, q0=2.5, rival=1.2, floor=1.0):
    exposures = [0.0] * k            # per-person exposures per creative
    clicks = spend = 0.0; served = 0; last_served = -1; dropped_at = None
    for w in range(WEEKS):
        c = w % k                    # rotate creatives week by week
        q = q0 * decay ** exposures[c]
        rank = bid * q
        if rank >= floor and rank > rival:
            price = rival / q + 0.01
            n = PEOPLE * IMPS * 0.01 * q          # clicks = impressions * 1% * quality
            clicks += n; spend += n * price; served += 1; last_served = w
            exposures[c] += IMPS
        elif dropped_at is None:
            dropped_at = w
    return clicks, spend, served, dropped_at

res = {}
for decay in (0.85, 0.99):
    for name, bid, k in (('single', 1.0, 1), ('single-2xbid', 2.0, 1), ('rotate6', 1.0, 6)):
        c, s, served, dropped = campaign(decay, bid, k)
        res[(decay, name)] = (c, s, served, dropped)
        print("decay %.2f %-13s clicks %7.1f spend %7.1f cpc %.3f weeks-served %2d first-drop-week %s" % (
            decay, name, c, s, (s / c if c else 0), served, dropped))
a = {n: res[(0.85, n)] for n in ('single', 'single-2xbid', 'rotate6')}
b = {n: res[(0.99, n)] for n in ('single', 'single-2xbid', 'rotate6')}
p1 = a['single'][3] is not None and a['single'][3] <= 2 and a['single'][0] < min(a['single-2xbid'][0], a['rotate6'][0])
p2 = a['single-2xbid'][2] == a['single'][2] + 1
p3 = a['rotate6'][0] >= 3 * a['single-2xbid'][0] and (a['rotate6'][1] / a['rotate6'][0]) <= (a['single-2xbid'][1] / a['single-2xbid'][0])
vals = [b[n][0] for n in b]
p4 = (max(vals) - min(vals)) / max(vals) <= 0.10
print("single drop-out week:", a['single'][3], "| served weeks single/2x/rot6:", a['single'][2], a['single-2xbid'][2], a['rotate6'][2])
# P5: after drop-out a single creative stays out
p5 = a['single'][2] == a['single'][3] if a['single'][3] is not None else False
print("PREDICTIONS held:", p1, p2, p3, p4, p5)
print("RESULT: %s decay0.85 clicks single/2xbid/rotate6=%.0f/%.0f/%.0f weeks=%d/%d/%d; decay0.99 clicks spread=%.1f%% (held %d/5)" % (
    "PASS" if all([p1, p2, p3, p4, p5]) else "FAIL", a['single'][0], a['single-2xbid'][0], a['rotate6'][0],
    a['single'][2], a['single-2xbid'][2], a['rotate6'][2], 100 * (max(vals) - min(vals)) / max(vals), sum([p1, p2, p3, p4, p5])))
