# Beats 0..8. A question (gap) opens at beat 0 and the answer lands at `answer_at`.
# The gap survives into beat t only if the link into t is causal (because/therefore)
# AND beat t is derived from the game (game-of-scene column); otherwise the viewer's question resets.
def tension(answer_at, links, derived):
    alive = 0
    for t in range(0, answer_at):
        if t > 0 and (links[t] != "causal" or not derived[t]): break
        alive += 1
    return alive
N = 9
causal = ["-"] + ["causal"] * 8
and_then = ["-"] + ["causal", "causal", "andthen", "causal", "andthen", "causal", "andthen", "causal"]
all_derived = [True] * N
stock = [True, True, True, True, False, True, True, True, True]  # one beat is a new noun not derived from the game
def content_facts(answer_at): return N  # same facts revealed in the whole short, any order
cases = {
    "early_reveal": tension(1, causal, all_derived),
    "withheld_chained": tension(8, causal, all_derived),
    "withheld_andthen_x3": tension(8, and_then, all_derived),
    "withheld_chained_one_nonderived": tension(8, causal, stock),
    "content_metric_early_vs_withheld": content_facts(1) - content_facts(8),
}
for k, v in cases.items(): print(k, v)
ok = (cases["early_reveal"] == 1 and cases["withheld_chained"] == 8 and cases["withheld_andthen_x3"] == 3
      and cases["withheld_chained_one_nonderived"] == 4 and cases["content_metric_early_vs_withheld"] == 0)
print("RESULT: %s gap beat-units early=%d withheld+chained=%d and-then=%d nonderived=%d; content metric difference %d" % (
    "PASS" if ok else "FAIL", cases["early_reveal"], cases["withheld_chained"], cases["withheld_andthen_x3"],
    cases["withheld_chained_one_nonderived"], cases["content_metric_early_vs_withheld"]))
