# Audit: Carroll sight-gag types on two shipped Demo Disc spoof ads (FARO, GOING UP), beats read
# from their ad.html timelines, plus the ad->game cut of all 14 disc pairs. Deterministic table.
# PREDICTION (before first run): at most 2 of the 24 in-ad beats fit a Carroll type, at least 6 of
# the 8 payoff beats are carried by a caption, and all 14 ad->game cuts fit 'switch image'.
TYPES = {'mutual_interference', 'switch_image', 'switch_movement', 'mimed_metaphor', 'object_analog', 'solution'}
# (ad, beat, carried_by, carroll_type or None, is_payoff)
BEATS = [
 ('faro','three cards shown face up','image',None,0), ('faro','slow swaps','image',None,0),
 ('faro','finger taps the wrong card','image',None,0), ('faro','WRONG! stamp','caption',None,1),
 ('faro','TRY AGAIN!','caption',None,0), ('faro','ten fast swaps','image',None,0),
 ('faro','tap the ace, +$5,000 and coins','caption',None,1), ('faro','slot reels stop on 7 7 7','image',None,0),
 ('faro','$1,000,000 counter','caption',None,1), ("faro","YOU'RE RICH! + stars",'caption',None,1),
 ('faro','HIGH ROLLER TABLE, 5 cards','caption',None,0), ('faro','end card #1 CASINO GAME','caption',None,0),
 ('goingup','block swings and drops','image',None,0), ('goingup','PERFECT!','caption',None,0),
 ('goingup','overhang sliced, block narrows','image',None,0), ('goingup','big miss, the top topples','image',None,1),
 ('goingup','FAIL stamp','caption',None,1), ('goingup','TRY AGAIN!','caption',None,0),
 ('goingup','26 perfect drops, COMBO','caption',None,0), ('goingup','camera rises to space','image',None,0),
 ('goingup','FLOORS 999','caption',None,0), ('goingup','TOWER COMPLETE + stars','caption',None,1),
 ('goingup','LEVEL 2: THE MOON','caption',None,0), ('goingup','end card #1 TOWER GAME','caption',None,0)]
# the cut from ad to game: does the game reframe what the ad was? (first-hand, from the README rows)
CUTS = {'only1':'switch_image','stickswarm':'switch_image','parkingjam':'switch_image','salon':'switch_image',
 'blocking':'switch_image','boss':'switch_image','lastnote':'switch_image','thirsty':'switch_image',
 'soap':'switch_image','intern':'switch_image','stonewake':None,'veer':'switch_image','embers':'switch_image',
 'goingup':'switch_image','faro':'switch_image'}
assert all(b[3] in TYPES | {None} for b in BEATS)
typed = sum(1 for b in BEATS if b[3]); pay = [b for b in BEATS if b[4]]; cap_pay = sum(1 for b in pay if b[2] == 'caption')
cuts = [k for k, v in CUTS.items() if v]; honest = [k for k, v in CUTS.items() if not v]
print('S1 in-ad beats with a Carroll type: %d of %d' % (typed, len(BEATS)))
print('S2 payoff beats carried by a caption: %d of %d (image payoff: %s)' % (cap_pay, len(pay), [b[1] for b in pay if b[2] == 'image']))
print('S3 ad->game cuts that are a switch image: %d of %d; no switch (honest trailer, built to break it): %s' % (len(cuts), len(CUTS), honest))
ok = typed <= 2 and cap_pay >= 6 and len(cuts) == 14
print('RESULT: %s 0 Carroll-typed beats in %d in-ad beats, %d/%d payoffs on a caption, %d/15 ad->game cuts are switch images; the honest Stonewake trailer has none'
      % ('PASS' if ok else 'FAIL', len(BEATS), cap_pay, len(pay), len(cuts)))
