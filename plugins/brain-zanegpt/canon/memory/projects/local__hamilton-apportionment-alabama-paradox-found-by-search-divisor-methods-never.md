# local/hamilton-apportionment-alabama-paradox-found-by-search-divisor-methods-never — lessons

Project: local/hamilton-apportionment-alabama-paradox-found-by-search-divisor-methods-never. Newest first.

---

## E1 — hamilton apportionment alabama paradox found by search divisor methods never
- Date: 2026-10-18
- Project: local/hamilton-apportionment-alabama-paradox-found-by-search-divisor-methods-never
- Tags: [apportionment][testing][voting]
- What: In seat apportionment, the largest-remainder (Hamilton) method loses a seat for a state when the house grows by one in 16014 of the tested 3-state populations and house sizes, e.g. populations 1, 3, 3 go from 1,1,1 seats at house 3 to 0,2,2 at house 4, while highest-averages divisor methods (Webster, Jefferson) showed 0 such cases; the price of the divisor methods is quota: Webster broke quota in 348 four-state cases, 151 of them with no tie.
- Why built: New domain seed from a real source, the Alabama paradox of the 1880 US census apportionment, to check by search that the paradox is a property of the method and to see what the monotone methods give up.
- Design: Exact Fractions, no RNG. Hamilton gives floors then the extra seats by largest remainder with index tie-break; Webster and Jefferson allocate seat by seat to the largest pop/(2s+1) or pop/(s+1). 3 states with populations 1..45 sorted and house 3..40 checked for any state losing seats from h to h+1; then 4 states, populations 1..18, house 4..30, quota check floor/ceil of exact share with a tie detector.
- Got right: Hamilton paradox found 16014 times and never violated quota; Webster and Jefferson never lost a seat when the house grew; the first quota check on 3 states predicted a Webster violation and found none, which sent the search to 4 states where it appeared.
- Where/why it failed: My prediction of a Webster quota violation in the 3-state scan was wrong (0 cases); the first 4-state violation, populations 1,1,1,3 at house 4, turned out to be a priority tie broken by index, so 197 of the 348 violations were tie artifacts and only the 151 tie-free ones count.
- Fix: When testing quota for a divisor method, count only tie-free allocations and use at least 4 states; when choosing a method, take house-monotone divisor methods if no state may lose a seat on growth and accept quota violations, or take Hamilton and accept the paradox.
- Why this fix: Sequential highest-averages allocation is house-monotone by construction (the sandbox mostly confirms the implementation), so the real tradeoff is that no method gets both quota and house monotonicity.
- Rule of thumb: A largest-remainder allocation can take a seat away when the house grows, so test house monotonicity by exhaustive small search before trusting it; divisor methods avoid that but can break quota, and ties must be excluded when counting violations.
- Provenance (verified/assumed): Verified first-hand by running the saved sandbox; small integer populations only, equal-weight states, the real 1880 census figures were not used and the divisor-method monotonicity is close to definitional.
- Composed: N/A
- Polarity: compatible
- Sandbox: sandboxes/2026-10-18__hamilton-apportionment-alabama-paradox-found-by-search-divisor-methods-never.py
- Prediction: At least 50 Hamilton paradox cases on 3 states, zero for Webster and Jefferson, zero Hamilton quota violations, at least one Webster quota violation (the last part was wrong on 3 states and re-tested on 4 states).
- Observed: RESULT: PASS Hamilton Alabama-paradox cases 16014 (first ([1, 3, 3], 3, [1, 1, 1], 4, [0, 2, 2])), Webster 0, Jefferson 0; quota violations hamilton 0 webster3 0 webster4 348 (tie-free 151)
- Scenarios: 1) 3 states Hamilton paradox search; 2) 3 states Webster and Jefferson monotonicity; 3) BREAK: Webster quota on 3 states predicted a violation and found none; 4) 4 states Webster quota with tie detector
- Link: scheduled brain train auto loop 1 pass 6; session_014AVjf81yxBZXZ5b84ovVC5

