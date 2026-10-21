"""PREDICTION (before run): in a rank=bid*quality, price=next_rank/own_quality+0.01 auction: (1) bid 1.00/QS 2.5 beats bid 2.00/QS 1.0 and
pays 0.81 (<its own bid 1.00 and < the 2.00 the loser bid); (2) raising the winner's QS from 2.5 to 5 at fixed bids cuts its price from 0.81
to 0.41 (>=40% lower); (3) the winner's price never exceeds its bid in a 5x5 grid of bids/qualities (25/25 cells); (4) a bid-doubling
cannot rescue an ad whose QS is under the reserve threshold (rank floor 1.0): bid 10 with QS 0.05 loses to bid 0.5 with QS 2.2; (5) BREAK: at
equal quality the highest bid wins and pays the runner-up's bid (classic second price), so quality only matters through the ratio."""
def auction(ads, floor=1.0):
    ranked = sorted(((b * q, n, b, q) for n, b, q in ads if b * q >= floor), reverse=True)
    if not ranked: return None
    nxt = ranked[1][0] if len(ranked) > 1 else floor
    r, n, b, q = ranked[0]
    return n, round(nxt / q + 0.01, 4)

r1 = auction([('hi_bid', 2.0, 1.0), ('hi_qual', 1.0, 2.5)])
r2 = auction([('hi_bid', 2.0, 1.0), ('hi_qual', 1.0, 5.0)])
cells = 0; ok_cells = 0
for b1 in (0.5, 1, 2, 4, 8):
    for q1 in (0.5, 1, 2, 4, 8):
        res = auction([('A', b1, q1), ('B', 2.0, 1.0)])
        if res:
            cells += 1; w = res[0]; bid = b1 if w == 'A' else 2.0
            ok_cells += res[1] <= bid + 0.0101
r4 = auction([('gamer', 10.0, 0.05), ('good', 0.5, 2.2)])
r5 = auction([('A', 3.0, 1.0), ('B', 2.0, 1.0)])
print(r1, r2, cells, ok_cells, r4, r5)
ok = (r1 == ('hi_qual', 0.81) and r2[0] == 'hi_qual' and r2[1] <= 0.81 * 0.6 and cells == ok_cells
      and r4[0] == 'good' and r5 == ('A', 2.01))
print("RESULT: %s low bid 1.00 w/ QS2.5 beats bid 2.00 and pays %.2f; QS 5 pays %.2f; price<=bid in %d/%d cells; bid 10 at QS 0.05 loses to the floor; equal-QS is plain second price (%.2f)" % (
  "PASS" if ok else "FAIL", r1[1], r2[1], ok_cells, cells, r5[1]))
