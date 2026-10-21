"""A story a day (The StoryTeller: A Story Short). Deterministic, stdlib. The king wants one
story a day for a year; the teller has a stock of 300. Policies: stop when the stock runs out,
repeat old stories, or tell the day itself (an event that happened today). Repeats are measured
as exact-duplicate share (the AI-video kernel's mass-produced template signal). BREAK: idle days
produce no event."""
def run(policy, stock=300, active=lambda d: True, days=365):
    told, out_day = [], None
    for d in range(days):
        if d < stock:
            told.append(f"stock-{d}")
        elif policy == "stop":
            out_day = d; break
        elif policy == "repeat":
            told.append(f"stock-{d % stock}")
        elif policy == "today":
            if active(d):
                told.append(f"day-{d}")
            else:
                out_day = d; break
    dup = 1 - len(set(told)) / len(told)
    return len(told), out_day, round(dup, 3)
stop = run("stop"); rep = run("repeat"); today = run("today")
idle = run("today", active=lambda d: d % 3 != 0)       # a teller who stays in two days of three
for k, v in (("stop", stop), ("repeat", rep), ("tell today", today), ("BREAK idle days", idle)):
    print(f"{k:16s} told={v[0]} ran_out_on_day={v[1]} duplicate_share={v[2]}")
ok = stop[1] == 300 and rep[2] > .15 and today == (365, None, 0.0) and idle[1] is not None and idle[1] < 365
print(("RESULT: PASS " if ok else "RESULT: FAIL ") + f"stock alone runs out on day {stop[1]}; repeating fills the year but {rep[2]:.0%} "
      f"of it is duplicates; telling the day covers all 365 with 0 duplicates; on a schedule with idle days it fails on day {idle[1]}")
