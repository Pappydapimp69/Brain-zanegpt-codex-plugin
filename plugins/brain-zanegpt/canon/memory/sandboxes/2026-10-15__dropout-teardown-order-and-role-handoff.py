# Model of local-player removal: teardown ORDER decides whether the pawn survives
# for AI adoption; role-bound pawns stay load-bearing only if the AI can hold the info.
def teardown(order, destroy_pawn=False):
    w = {"pawn": "alive", "ctrl": "player", "ai": None}
    def unpossess(): 
        if w["pawn"] == "alive": w["ctrl"] = None
    def parent_destroyed():            # engine path: PawnLeavingGame kills the pawn
        w["pawn"] = "pending_kill"
    def adopt():
        if w["pawn"] == "alive" and w["ctrl"] is None: w["ai"] = "bot"; w["ctrl"] = "ai"
    if destroy_pawn: parent_destroyed()
    elif order == "unpossess_then_parent": unpossess(); parent_destroyed_guard = None; adopt_now = True; adopt(); 
    elif order == "parent_then_unpossess": parent_destroyed(); unpossess(); adopt()
    elif order == "default": parent_destroyed(); adopt()
    return w
def outcome(w): return "adopted" if w["ai"] else ("vanished" if w["pawn"]!="alive" else "orphaned")
cases = {"bDestroyPawn=true": teardown("x", True),
         "default": teardown("default"),
         "parent_then_unpossess": teardown("parent_then_unpossess"),
         "unpossess_then_parent": teardown("unpossess_then_parent")}
for k,v in cases.items(): print(f"{k:24s} -> {outcome(v)}")
# party-size keyed rule (mirage/E18): lose when active actors < 4 of 6
def party(adopted): return 6 if adopted else 5
# reactive pacing: inject complication when team progress >= 0.8 of target
def pacing(progress_per_actor, n, target=5.0): return progress_per_actor*n >= target*0.8
okset = {k: outcome(v) for k,v in cases.items()}
adopted_ok = okset["unpossess_then_parent"]=="adopted"
others_fail = all(okset[k]!="adopted" for k in ("bDestroyPawn=true","default","parent_then_unpossess"))
size_kept = party(adopted_ok)==6 and party(False)==5
# BREAK: the asymmetric-role pawn. Adopted AI cannot read the private manual.
roles = {"defuser":{"info":"bomb"},"expert":{"info":"manual"}}
def role_load_bearing(adopt_ai):                 # does the team still need BOTH info holders?
    holders = {"bomb"} | ({"manual"} if not adopt_ai else set())
    return holders
bomb_only = role_load_bearing(True)
role_hollow = "manual" not in bomb_only
# pacing signal: with an AI-held expert the team's measured progress is the human's only,
# so the strong-performance trigger fires late/never
fires_full = pacing(1.0, 4)           # 4 humans each 1.0 -> 4 >= 4 True
fires_hollow = pacing(1.0, 3)         # one human replaced by non-contributing bot -> 3 < 4
print("party size adopted/destroyed:", party(True), party(False), "| role hollow after adoption:", role_hollow, "| pacing fires full/hollow:", fires_full, fires_hollow)
ok = adopted_ok and others_fail and size_kept and role_hollow and fires_full and not fires_hollow
print("RESULT: %s only unpossess-before-parent adopts (1/4 orders), party size 6 vs 5, but an adopted AI leaves the info-holding role hollow and silences the pacing trigger (fires %s vs %s)" % ("PASS" if ok else "FAIL", fires_full, fires_hollow))
