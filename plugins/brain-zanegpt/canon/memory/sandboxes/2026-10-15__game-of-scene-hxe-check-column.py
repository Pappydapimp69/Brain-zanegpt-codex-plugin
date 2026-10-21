"""Sandbox: does the H/E/X check column of the game-of-the-scene beat sheet work?
PREDICTION (written before first run): the naive column (X = beat names any new unusual thing) flags
the planted second-game beat (scenario 2) and passes the clean sheet (1) with 0 false X, BUT it
(a) false-flags legitimate derived consequences (scenario 4, expect >=1 false X), (b) passes a flat
repeat sheet with 0 X (scenario 3), (c) passes a stock/hack premise (scenario 5), (d) passes a huge
intensity jump (scenario 6). Hidden assumption: 'new unusual thing' == 'new game'. Wrong if scenario 4
gets 0 false X or scenario 3 gets flagged by the plain H/E/X column."""
GAME = "dog_runs_the_bank"
STOCK = {"office_desk_evolution", "men_vs_women", "airline_food"}
# beat: (things_present_set_of_unusual, intensity, explains_why, derived_from_game)
def naive(sheet):
    seen, prev, out = {sheet["game"]}, 0, []
    for things, inten, why, derived in sheet["beats"]:
        new = set(things) - seen
        if new: out.append("X"); seen |= new
        elif why: out.append("E")
        elif inten > prev: out.append("H")
        else: out.append("-")   # H/E/X column has no label for flat; '-' shown only to count
        prev = max(prev, inten)
    return out
def fixed(sheet, max_step=3):
    seen, prev, out = {sheet["game"]}, 0, []
    for things, inten, why, derived in sheet["beats"]:
        new = set(things) - seen
        if new and not derived: out.append("X"); seen |= new
        elif why: out.append("E"); seen |= new
        elif inten - prev > max_step and prev: out.append("J")  # jump: too far to cohere
        elif inten > prev: out.append("H"); seen |= new
        else: out.append("F")  # flat
        prev = max(prev, inten)
    pre = "STOCK" if sheet["game"] in STOCK else "ok"
    return out, pre
G = GAME
S = {
 1: dict(game=G, truth=["H","H","E","H"], beats=[([G],2,False,False),([G],4,False,False),([G],4,True,False),([G],6,False,False)]),
 2: dict(game=G, truth=["H","H","X","H"], beats=[([G],2,False,False),([G],4,False,False),([G,"alien_landing"],5,False,False),([G],6,False,False)]),
 3: dict(game=G, truth=["H","F","F","F"], beats=[([G],3,False,False),([G],3,False,False),([G],3,False,False),([G],3,False,False)]),
 4: dict(game=G, truth=["H","H","H","H"], beats=[([G],2,False,False),([G,"loan_forms_in_bark"],4,False,True),([G,"vault_of_bones"],5,False,True),([G],7,False,False)]),
 5: dict(game="office_desk_evolution", truth=["H","H","H","H"], beats=[(["office_desk_evolution"],i,False,False) for i in (2,4,5,6)]),
 6: dict(game=G, truth=["H","J","H","H"], beats=[([G],1,False,False),([G],9,False,False),([G],9.5,False,False),([G],10,False,False)]),
}
tot = {"naive":0,"fixed":0}; n=0; res={}
for k,s in S.items():
    nv = [("F" if x=="-" else x) for x in naive(s)]
    fx, pre = fixed(s)
    # score: does the column's label sequence equal truth?
    nvx = nv
    res[k]=(nvx==s["truth"], fx==s["truth"], pre)
    print(k, "truth", "".join(s["truth"]), "naive", "".join(nv), "fixed", "".join(fx), pre)
nm = sum(1 for v in res.values() if v[0]); fm = sum(1 for v in res.values() if v[1])
falseX = sum(1 for k in S if "X" in naive(S[k]) and "X" not in S[k]["truth"])
print("naive exact", nm, "/6 fixed exact", fm, "/6; naive false-X sheets", falseX, "; stock premise caught only by separate check:", res[5][2])
# note: naive '-' relabelled F post hoc only for scoring; the real H/E/X column prints '-' i.e. unlabelled flat/jump
plain_flat_flagged = "X" in naive(S[3])
ok = (res[1][0] and fm==6 and nm<6 and falseX>=1 and not plain_flat_flagged and res[5][2]=="STOCK")
print("RESULT: %s naive exact %d/6, fixed(derived-link + F/J labels + stock check) %d/6, false-X %d, flat flagged by plain column=%s" % ("PASS" if ok else "FAIL", nm, fm, falseX, plain_flat_flagged))
