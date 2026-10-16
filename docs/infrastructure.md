# Infrastructure

Setup, dependencies, data, commands and git notes. Commands run from the repo root, `C:\Projects\MLQuity`.

## Environment

- Python 3.12 or newer. Developed and tested on Python 3.14.7, Windows 11.
- Virtual environment in `.venv/` (git-ignored).

```
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

- Point the IDE at `.venv\Scripts\python.exe`. The commands below call that interpreter directly, so they work without activating the venv.
- Offline install (from the README):

```
pip download -r requirements.txt -d wheels\
pip install --no-index --find-links wheels -r requirements.txt
```

## Dependencies

`requirements.txt` pins every direct dependency with `==`. Packages marked *planned* are not imported by any code yet.

| Group | Packages | Used for | Status |
|-------|----------|----------|--------|
| Core | numpy 2.5.4, pandas 3.0.6, scipy 1.18.1, pyarrow 26.0.0 | Arrays, frames, parquet I/O | numpy and pandas in use; scipy and pyarrow planned |
| Statistics | statsmodels 0.15.0 | ADF test for fracdiff | planned (Phase 3) |
| Modeling | scikit-learn 1.9.1, lightgbm 4.7.0 | Ensemble baseline, importance | planned (Phase 5) |
| Data download | requests 2.34.2 | `download_data.py` | in use |
| Notebooks | matplotlib 3.11.2, jupyterlab 4.6.4 | `notebooks/` | planned |
| Tests | pytest 9.1.1 | `tests/` | in use |

Adding or upgrading a dependency needs the owner's approval.

## Data

- **Source:** Tiingo daily prices, `https://api.tiingo.com/tiingo/daily/{ticker}/prices`, authenticated with the header `Authorization: Token <key>`.
- **API key:** put it in `tiingo_key.txt` in the repo root. The file holds one line and is git-ignored. `download_data.py` reads it as UTF-8 with BOM handling, so a file saved by Notepad works.
- **Download settings** are constants at the top of `download_data.py`: `TICKERS = ["SPY"]`, `START_DATE = "2020-01-01"`, `END_DATE = "2026-10-01"`.
- **Raw output:** `data/raw/{ticker}.csv` with columns `date`, `close` (Tiingo `adjClose`) and `volume` (Tiingo `adjVolume`). Git-ignored. Never edit it by hand.
- **Processed output:**
  - `data/processed/trials/trial_NNNN.csv`: one daily-returns file per trial, column `return`. Git-ignored.
  - `data/processed/trials/trials.csv`: one row per trial. Tracked by git, and append-only by design.

## Commands

| Task | Command | Side effects |
|------|---------|--------------|
| Run tests | `.venv\Scripts\python.exe -m pytest` | None. Tests use temporary folders and no network. About 0.5 s. |
| Download SPY | `.venv\Scripts\python.exe download_data.py` | Overwrites `data/raw/SPY.csv`. Needs `tiingo_key.txt`. |
| Run baseline backtests | `.venv\Scripts\python.exe run_backtest.py` | Appends 6 rows to `trials.csv` and writes 6 trial files. Each run adds trials, even for repeated configs. |

`download_data.py` uses relative paths (`tiingo_key.txt`, `data/raw`). Run it from the repo root, or it will look for the key in the wrong folder.

## Git

- Branch: `main`. Remote: `origin`.
- `core.autocrlf` is `true` on this machine. Files are stored with LF, and git converts them to CRLF. You will see `LF will be replaced by CRLF` warnings. They are expected. There is no `.gitattributes` file.
- Git-ignored (see `.gitignore`):
  - `.venv/`, `__pycache__/`, `.pytest_cache/`
  - `data/raw/`, and everything under `data/processed/` except `trials/trials.csv`
  - `*.csv` in general, with the `trials.csv` exception. A new CSV that should be tracked needs its own `!` line.
  - `tiingo_key.txt`, `.env`, IDE folders
- Commit messages: one line, past tense or plain statement, ending with a period. Examples in history: `Added tests and transactional costs.`, `Data fetching and loading working.`

## Tests

- pytest collects `tests/` and reads the root `conftest.py`.
- 29 tests, all passing at the time of writing.
- Shared test helpers: `tests/fake_data.py` (`make_prices`).
