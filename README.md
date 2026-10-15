# MLQuity

A follow-along build of López de Prado's *Advances in Financial Machine Learning* (AFML), applied to US equities on daily bars. Each phase pairs one or two book chapters with one module to build.

Read the chapter first, then build the module. Skip the microstructure material (Ch 19 and related).

## Project layout

```
MLQuity/
├── data/
│   ├── raw/            # raw data, never edited
│   └── processed/
├── src/
│   ├── data.py         # loading, point-in-time handling
│   ├── features.py     # fracdiff + standard features          (Ch 5)
│   ├── labeling.py     # CUSUM (Ch 2), triple-barrier, meta-labeling (Ch 3)
│   ├── weights.py      # uniqueness, time-decay                (Ch 4)
│   ├── cv.py           # PurgedKFold, embargo, CPCV            (Ch 7, 12)
│   ├── importance.py   # MDI, MDA, SFI                         (Ch 8)
│   ├── sizing.py       # probability -> position size          (Ch 10)
│   ├── backtest.py     # bets -> daily positions -> returns, CPCV (Ch 10, 12)
│   ├── stats.py        # Sharpe, PSR, DSR, PBO                 (Ch 11, 12, 14)
│   └── trials.py       # log_trial(): trials.csv + each trial's returns
├── notebooks/          # one per phase, exploration only
├── tests/              # unit tests for every src module, plus fake_data.py
├── trials.csv          # log of EVERY config tried (needed for DSR)
├── requirements.txt    # pinned dependencies
└── README.md
```

## Setup

Requires Python 3.12 or newer (developed and verified on 3.14).

```
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

Then point your editor at the interpreter at `.venv/Scripts/python.exe` (PyCharm: Settings → Project → Python Interpreter → Add Local Interpreter → Existing; VS Code: Ctrl+Shift+P → "Python: Select Interpreter"). PyCharm usually detects `.venv` in the project root automatically.

To install on a machine without internet, pre-download the packages first:

```
pip download -r requirements.txt -d wheels\
pip install --no-index --find-links wheels -r requirements.txt
```

## Phases

| # | Read | Build | Done when |
|---|------|-------|-----------|
| 0 | Ch 1-2 (skim) | Data loader, repo skeleton, baseline strategies (buy-and-hold, simple momentum), `trials.csv` | Baseline backtest runs end to end |
| 1 | Ch 2 §2.5 (CUSUM), Ch 3 | CUSUM filter, daily volatility, triple-barrier labels, then meta-labeling | Label counts and class balance look sane; unit tests pass |
| 2 | Ch 4 | Concurrency, average uniqueness, sample weights | Weights verified on a toy example by hand |
| 3 | Ch 5 | Fixed-width fracdiff, plus the minimum `d` that passes ADF | Features stationary but still correlated with price |
| 4 | Ch 7 | PurgedKFold with embargo | Test shows no label overlap leaking between train and test |
| 5 | Ch 6 (skim), Ch 8 | LightGBM baseline, MDI/MDA/SFI | Importance is stable across folds, not noise |
| 6 | Ch 10 | Probability-based sizing, discretization | Sized strategy compared against fixed-size |
| 7 | Ch 11, 12, 14 | CPCV backtest, PSR, DSR, PBO | A distribution of Sharpe ratios, not one number |
| 8 | (none) | Capstone: run the whole pipeline on fake random data, plant a leak, measure power | Pipeline finds nothing in noise and detects a planted leak |

## Chapter map

| Ch | Topic | Where it lands |
|----|-------|----------------|
| 1-2 | Financial ML as a subject; financial data structures (bars); CUSUM filter (§2.5.2.1) | Phase 0 (skim), CUSUM in Phase 1 |
| 3 | Labeling (CUSUM, triple-barrier, meta-labels) | Phase 1 |
| 4 | Sample weights (concurrency, uniqueness, time-decay) | Phase 2 |
| 5 | Fractionally differentiated features | Phase 3 |
| 6 | Ensemble methods | Phase 5 (skim) |
| 7 | Cross-validation in finance (purging, embargo) | Phase 4 |
| 8 | Feature importance (MDI, MDA, SFI) | Phase 5 |
| 10 | Bet sizing | Phase 6 |
| 11 | The dangers of backtesting | Phase 7 |
| 12 | Backtesting through cross-validation (CPCV) | Phase 7 |
| 13 | Backtesting on synthetic data | Skip |
| 14 | Backtest statistics (PSR, DSR) | Phase 7 |

## Notes and open questions

These are points to settle before or during the build, not blockers.

1. **Start `trials.csv` in Phase 0.** The Deflated Sharpe Ratio needs the total number of configurations tried. Retroactive logging is unreliable. Log discarded configs too, not only the winner.
2. **Daily bars limit sample size.** CUSUM and triple-barrier on daily data produce few events per year, so expect wide confidence intervals from Phase 5 onward. Decide the universe size and history length early, since they drive this more than any model choice.
3. **Survivorship bias.** The Phase 0 loader must include delisted tickers and use point-in-time index membership. Without this, backtests will look better than they are, and the error will be invisible in later phases.
4. **Verify chapter numbers against your copy.** Section titles for Ch 10 (Bet Sizing), Ch 11 (The Dangers of Backtesting) and Ch 12 (Backtesting through Cross-Validation) were checked against a published table of contents. Everything else follows the book's numbering as recalled, and snippet numbers are the least reliable. Check against your table of contents, especially where DSR and PBO sit among Ch 11, 12 and 14. README.html tags each reference as checked or from memory.
5. **Expect little statistical power.** One stock on daily bars gives a few hundred events. On fake random data the Sharpe ratio of the finished pipeline varied by about 0.4 from luck alone, and a planted modest effect was often invisible. Phase 8 measures this. A Sharpe above about 1.5 on one stock is more likely a bug than an edge.
