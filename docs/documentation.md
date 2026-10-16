# Documentation log

Every change to the repo gets an entry here, newest first. Add the entry in the same response as the change. Use this template:

```
## YYYY-MM-DD: short title
- **Changed:** what changed, in one or two lines
- **Files:** paths touched
- **Why:** reason, if not obvious
```

## 2026-10-16: Agent guide and docs added

- **Changed:** Added `AGENTS.md` (agent rules, repo summary, doc index) and `CLAUDE.md` (imports `AGENTS.md` so Claude Code loads the rules). Added `docs/infrastructure.md`, `docs/coding.md` and this file. No code changed.
- **Files:** `AGENTS.md`, `CLAUDE.md`, `docs/infrastructure.md`, `docs/coding.md`, `docs/documentation.md`
- **Why:** Agents need a map of the repo and explicit rules, including no code changes unless asked.

## Known issues

Open items, not fixed. When one is fixed, add a changelog entry above and remove it here.

1. **The trial log has duplicates and gaps.** `trials.csv` has rows for trial IDs 5, 6, 7, 8, 11 and 12.
   - Rows 5 and 8 have the same config (buy-and-hold, 5 bps) and identical results.
   - Rows 6 and 11 have the same config (momentum, 5 bps) and identical results.
   - Trials 9 and 10 have trial files but no rows.
   - The files for trials 1 to 6 are missing, although rows 5 and 6 point to them.
   - Each run of `run_backtest.py` logs 6 trials even when the configs repeat, so re-runs inflate the trial count that the Deflated Sharpe Ratio depends on.
   - Decide the logging policy before the next run. Options include one row per distinct config, or logging every attempt with a flag.
2. **Trial ids can be reused.** `next_trial_id()` takes the largest id in `trials.csv` plus one. If the last row is deleted, the next run reuses its id and overwrites the old `trial_NNNN.csv` without warning.
3. **`log_trial` is not atomic.** It writes the returns file before appending the row. If the append fails, an orphan file is left behind. This may explain issue 1. Not verified.
4. **`download_data.py` uses relative paths.** Run from any folder other than the repo root, it looks for the key in the wrong place and creates `data/raw` there.
5. **Stale comment in `tests/test_backtest.py`.** `test_sharpe_per_period_is_not_annualised` says it fails until `sharpe()` takes a `periods` argument. It already does, and the test passes.
