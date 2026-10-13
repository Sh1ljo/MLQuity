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
│   ├── labeling.py     # CUSUM, triple-barrier, meta-labeling  (Ch 3)
│   ├── weights.py      # uniqueness, time-decay                (Ch 4)
│   ├── cv.py           # PurgedKFold, embargo, CPCV            (Ch 7, 12)
│   ├── importance.py   # MDI, MDA, SFI                         (Ch 8)
│   ├── sizing.py       # probability -> position size          (Ch 10)
│   ├── backtest.py     # event-driven daily backtest
│   └── stats.py        # Sharpe, PSR, DSR, PBO                 (Ch 11, 14)
├── notebooks/          # one per phase, exploration only
├── tests/              # unit tests for every src module
├── trials.csv          # log of EVERY config tried (needed for DSR)
└── README.md
```

## Phases

| # | Read | Build | Done when |
|---|------|-------|-----------|
| 0 | Ch 1-2 (skim) | Data loader, repo skeleton, baseline strategies (buy-and-hold, simple momentum), `trials.csv` | Baseline backtest runs end to end |
| 1 | Ch 3 | CUSUM filter, daily volatility, triple-barrier labels, then meta-labeling | Label counts and class balance look sane; unit tests pass |
| 2 | Ch 4 | Concurrency, average uniqueness, sample weights | Weights verified on a toy example by hand |
| 3 | Ch 5 | Fixed-width fracdiff, plus the minimum `d` that passes ADF | Features stationary but still correlated with price |
| 4 | Ch 7 | PurgedKFold with embargo | Test shows no label overlap leaking between train and test |
| 5 | Ch 6 (skim), Ch 8 | LightGBM baseline, MDI/MDA/SFI | Importance is stable across folds, not noise |
| 6 | Ch 10 | Probability-based sizing, discretization | Sized strategy compared against fixed-size |
| 7 | Ch 11, 12, 14 | CPCV backtest, PSR, DSR, PBO | A distribution of Sharpe ratios, not one number |

## Chapter map

| Ch | Topic | Where it lands |
|----|-------|----------------|
| 1-2 | Financial ML as a subject; financial data structures (bars) | Phase 0 (skim) |
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
4. **Verify chapter numbers against your copy.** The chapter map above follows the book's standard numbering as recalled. Check it against your table of contents before relying on it, especially the split of DSR and PBO between Ch 11, 12 and 14.
