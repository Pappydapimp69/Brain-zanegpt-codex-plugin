"""Trapping a necessary sink (The StoryTeller: The Soldier and Death, from the Russian tale in
Afanasyev retold by Ransome). Deterministic, stdlib. A village gains 10 people a year (faucet);
everyone ages a year each year (starting from an existing village, ages 0-79); Death takes everyone at age 80 (sink).
From year 40 Death is in the sack for 20 years, then released. Coverage = deaths / births
(the economy kernel's faucet/sink ratio). 'Waiting' = people past 80 who cannot die."""
def run(trap=(40, 60), aging=True, years=100):
    pop = [a for a in range(80) for _ in range(10)]; log = []   # an existing village, ages 0-79
    for y in range(years):
        pop = [a + (1 if aging else 0) for a in pop] + [0] * 10
        trapped = trap and trap[0] <= y < trap[1]
        dead = 0 if trapped else sum(1 for a in pop if a >= 80)
        if not trapped:
            pop = [a for a in pop if a < 80]
        waiting = sum(1 for a in pop if a >= 80)
        log.append((y, dead / 10, waiting))
    return log
base = run(trap=None); trap = run(); still = run(aging=False)
cov_trap = [c for y, c, w in trap if 45 <= y < 60]; wait_end = trap[59][2]; after = trap[61][2]
cov_base = [c for y, c, w in base if 85 <= y < 100]
print(f"no trap: coverage {min(cov_base):.2f}-{max(cov_base):.2f}, waiting {base[70][2]}")
print(f"trapped 40-60: coverage {max(cov_trap):.2f}, waiting at year 59: {wait_end}, two years after release: {after}")
print(f"BREAK no aging, trapped: waiting at year 59: {still[59][2]}")
ok = max(cov_trap) == 0 and wait_end > 0 and after == 0 and still[59][2] == 0 and min(cov_base) >= .95
print(("RESULT: PASS " if ok else "RESULT: FAIL ") + f"with Death in the sack the sink's coverage drops from 1.00 to {max(cov_trap):.2f} and "
      f"{wait_end} people are left waiting by year 59, all cleared on release; with no aging the same trap leaves {still[59][2]} waiting")
