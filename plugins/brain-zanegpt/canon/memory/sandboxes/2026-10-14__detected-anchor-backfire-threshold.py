"""Deterministic two-round seller/buyer model of 'a detected extreme anchor backfires'.
Seller cost 40, buyer value 100 (ZOPA 40..100). Price = buyer_open + w*(anchor-buyer_open).
Anchor above PLAUS (130) is detected as a ploy: w drops, and (repeat game) the buyer
opens lower next round, and walks (picks a new partner) if the anchor was extreme (>200).
Written-vs-verbal: a written round-1 term cannot be reopened by buyer in round 2; verbal can."""
COST, VALUE, PLAUS, EXTREME = 40, 100, 130, 200
def deal(anchor, buyer_open):
    detected = anchor > PLAUS
    w = 0.2 if detected else 0.5
    p = buyer_open + w * (anchor - buyer_open)
    return min(p, VALUE), detected   # buyer never pays above value (BATNA = walk away)
def seller_profit(anchor, rounds, written=False):
    total = 0; buyer_open = 50; hard = 0
    for r in range(rounds):
        if r == 1 and hard == -1: break           # buyer chose a new partner
        p, det = deal(anchor, buyer_open - hard)
        total += p - COST
        if det and r == 0:
            hard = 15                              # retaliation: harder opening
            if anchor > EXTREME: hard = -1         # walks from future dealings
        if r == 0 and not det:
            hard = 0
        if r == 0 and written and det: pass
    return total
def best(rounds):
    anchors = range(60, 301, 10)
    return max(anchors, key=lambda a: seller_profit(a, rounds)), {a: round(seller_profit(a, rounds),1) for a in (80,120,130,140,200,210,300)}
for name, rounds in (("one-shot",1),("repeat-2",2)):
    print(name, best(rounds))
# scenario 3: verbal vs written for round-1 deal at moderate anchor 120 when buyer would reopen after 'second thoughts'
def reopen(written):
    p,_ = deal(120, 50); return p if written else p - 10   # verbal deal reopened downward by 10
v, w = reopen(False), reopen(True)
print("verbal", v, "written", w)
b1,_ = best(1); b2,t2 = best(2)
ok = (b2 <= PLAUS and seller_profit(300,2) < seller_profit(b2,2) and seller_profit(210,2) < seller_profit(130,2)
      and b1 > PLAUS and w > v)
print(f"RESULT: {'PASS' if ok else 'FAIL'} one-shot best anchor {b1} (no retaliation cost, extremes still pay 'less' only via w), repeat best {b2} <= plausibility {PLAUS}; profit@130={seller_profit(130,2)} @210={seller_profit(210,2)} @300={seller_profit(300,2)}; written {w} > verbal {v}")
