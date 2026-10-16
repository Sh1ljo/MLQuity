# MLQuity: agent guide

Read this file first. It covers the rules for agents, what each file does, and where the docs are.

## Rules for agents

The owner is building this project by hand. Your default role here is reviewer and explainer, not author.

1. **Do not change code unless the user asks for that change in the current message.** Code means `src/`, `tests/`, `run_backtest.py`, `download_data.py`, `conftest.py` and `requirements.txt`. Reading, reviewing, explaining and answering questions never need permission.
2. **Flag problems, do not fix them.** If you see a bug, a race condition or a wrong number, describe it and the fix you would make. Do not apply it.
3. **Do not run anything that changes data or the trial log without asking.** `run_backtest.py` appends 6 rows to `data/processed/trials/trials.csv` on every run. `download_data.py` overwrites `data/raw/SPY.csv`. Running `pytest` is safe: it uses temporary folders.
4. **Never edit `data/raw/`, and never edit `data/processed/trials/` by hand.** The trial log feeds the Deflated Sharpe Ratio, so a deleted or duplicated row changes the result. See [known issues](docs/documentation.md#known-issues).
5. **Do not commit, push, branch, stash or revert.** The working tree holds uncommitted changes from the owner. Leave them as they are.
6. **When asked to change code:**
   - read [docs/coding.md](docs/coding.md) and follow it;
   - make only the requested change, with no new dependencies and no new abstractions;
   - add an entry to [docs/documentation.md](docs/documentation.md) saying what changed, which files, and why;
   - if the file layout, setup or module summary changed, update the matching section of this file or of [docs/infrastructure.md](docs/infrastructure.md).
7. **Ask before writing code when the request is unclear.** Ask one or two specific questions, not a general "can you clarify".

## Documentation index

| File | What it holds |
|------|---------------|
| [README.md](README.md) | Project goal, phase plan, chapter map, open questions |
| [README.html](README.html) | Step-by-step coaching guide with book references |
| [docs/infrastructure.md](docs/infrastructure.md) | Setup, dependencies, data flow, commands, git and environment notes |
| [docs/coding.md](docs/coding.md) | Coding style used in this repo, and rules for new code |
| [docs/documentation.md](docs/documentation.md) | Log of every change, and known issues. Update it after each change. |

## What the project is

A follow-along build of López de Prado's *Advances in Financial Machine Learning* on US equities, daily bars. Each phase builds one module from the book.

**Status:** Phase 0 runs end to end (buy-and-hold and 252-day momentum on SPY, with trial logging). `pytest` passes 29 tests. The modules for Phases 1 to 8 are empty placeholders.

**Constraints that come from the README. Keep them in mind when reviewing or changing code:**

- Positions are decided at the close of day t and held from day t+1. This avoids lookahead. `run_backtest` enforces it with a one-day shift.
- Transaction costs are in basis points on turnover. The first entry counts as a trade.
- Sharpe ratio is annualised with `sqrt(252)`.
- Every configuration tried must be logged, including discarded ones. The Deflated Sharpe Ratio needs the total count.
- SPY only. Do not report results on a multi-ticker universe until survivorship bias is handled (README note 6).

## Repository layout and status

| Path | Status | What it does |
|------|--------|--------------|
| `src/data.py` | implemented | `load_prices(ticker="SPY")` reads `data/raw/{ticker}.csv`, indexes by date, and raises `ValueError` on duplicate dates, missing or non-positive closes, or a one-day move above 40 percent. |
| `src/backtest.py` | implemented | `buy_and_hold(prices)`. `momentum(prices, lookback=252)` gives 1.0 when the past return is positive, else 0.0. `run_backtest(positions, prices, cost_bps=0.0)` shifts positions one day and charges costs on turnover. `sharpe(returns, periods=252)` returns NaN when std is zero. `summarize(returns)` returns `n_days`, `total_return` and `sharpe`. |
| `src/trials.py` | implemented | `log_trial(config, returns)` writes `trial_NNNN.csv` and appends a row to `trials.csv`, then returns the trial id. `next_trial_id()` is the largest logged id plus one. |
| `run_backtest.py` | implemented | Runs buy-and-hold and momentum_252d on SPY at 0, 5 and 10 bps, and logs 6 trials per run. |
| `download_data.py` | implemented | Downloads daily prices from Tiingo for `TICKERS` into `data/raw/{ticker}.csv`. Needs `tiingo_key.txt` in the repo root. |
| `conftest.py` | implemented | Empty. It lets pytest import `src` from any launch directory. |
| `tests/` | implemented | `test_data.py`, `test_backtest.py`, `test_trials.py`. `fake_data.py` provides `make_prices(n, seed, drift)`, synthetic prices with volatility clustering. |
| `src/features.py`, `labeling.py`, `weights.py`, `cv.py`, `importance.py`, `sizing.py`, `stats.py` | empty | Placeholders for Phases 1 to 7. |
| `notebooks/` | empty | One notebook per phase, for exploration only. |
| `data/raw/` | git-ignored | Raw downloads. Never edited. |
| `data/processed/trials/` | partly tracked | `trials.csv` is tracked. `trial_NNNN.csv` files are git-ignored. |

## Main data flow

```
download_data.py ──> data/raw/SPY.csv
                        │
                 data.load_prices()
                        │
        backtest.buy_and_hold() / momentum()
                        │  positions
        backtest.run_backtest(positions, prices, cost_bps)
                        │  daily returns
        backtest.summarize()  +  trials.log_trial()
                        │
   data/processed/trials/trials.csv  +  trial_NNNN.csv
```

Setup and commands are in [docs/infrastructure.md](docs/infrastructure.md). Style rules are in [docs/coding.md](docs/coding.md).
