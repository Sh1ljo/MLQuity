# Coding style

This style is taken from the code the owner has already written in `src/`, `tests/` and the scripts. New code should look like it belongs next to it. When unsure, read `src/backtest.py` and `tests/test_backtest.py`.

## Files

- Every module starts with a one-line comment saying what it does, e.g. `# Loads prices from csv`. Test files start with `# Tests for src/<module>.py`.
- Imports go in this order, with a blank line between groups: standard library, third party, project.

```python
import pathlib

import pandas as pd

from src.backtest import summarize
```

- Use `import pandas as pd` and `import numpy as np`. Use `pathlib` for paths.
- Paths and settings that code or tests need to change are module-level constants in `UPPER_CASE`, such as `RAW_DIR` and `TRIALS_CSV`. Tests replace them with `monkeypatch`, so do not hard-code a path inside a function.
- Project-root paths are built from `__file__`: `ROOT = pathlib.Path(__file__).resolve().parents[1]`.
- Two blank lines between top-level functions.

## Functions

- Plain module-level functions. No classes, base classes, factories or decorators beyond pytest's. The code has none, and the global rules ask for none until there is a need.
- Type hints on public functions in `src/`:

```python
def sharpe(returns: pd.Series, periods: int = 252) -> float:
```

- Default values are written in the signature: `lookback: int = 252`, `cost_bps: float = 0.0`.
- Data types:
  - prices: a DataFrame with a `DatetimeIndex` and a `close` column;
  - positions and returns: a `pd.Series` of floats indexed by date;
  - summaries: a plain `dict`.
- Short bodies. A method chain is fine when it fits on one line, as in `pd.read_csv(path, parse_dates=["date"]).set_index("date").sort_index()`. Break longer work into named variables.
- Names are short and plain: `df`, `close`, `past_ret`, `asset_ret`, `held`, `cost`. Suffixes carry units or meaning: `cost_bps`, `sr_pp` (per period).
- `main()` with a `__name__` guard for scripts:

```python
def main() -> None:
    ...


if __name__ == "__main__":
    main()
```

## Comments

- Short plain-English comments above the code they describe. They say what the next lines do or why:

```python
# first entry counts as a trade
turnover = (held - held.shift(1, fill_value=0)).abs()
```

- Write units in words in comments ("40 percent", "5 bps") and in code as named variables.
- No docstrings in the existing code. Do not add them unless the owner asks.
- Keep comments short. Remove a comment that no longer matches the code.

## Errors and output

- Raise the specific built-in: `FileNotFoundError`, `ValueError`, `RuntimeError`. The message is an f-string that names the file, ticker or offending values:

```python
raise ValueError(f"Duplicate dates: {list(dupes)}")
```

- Validate at system boundaries: file loads and API responses. Do not hide a bad file with a fallback. Raise.
- An undefined statistic returns `np.nan`, as `sharpe()` does for zero standard deviation. It does not raise.
- Script output uses `print` with f-string formats: `{stats['total_return']:.4%}`, `{stats['sharpe']:.3f}`.
- Use readable literals: `100_000`. Basis points are divided by `10000` at the point of use.

## Tests

- One file per module: `tests/test_<module>.py`.
- Test names describe the behaviour in plain words: `test_momentum_flat_before_lookback`, `test_flat_position_pays_no_cost`, `test_round_trip_pays_entry_and_exit`.
- Put a comment above a test that checks a rule, and show the arithmetic when it is short:

```python
# Day 1 holds positions[0] = 0 -> flat. Day 2 holds positions[1] = 1.
```

- Use small hand-made series when the expected answer can be worked out by hand. Use `make_prices(n=...)` from `tests/fake_data.py` for longer random data. It takes a fixed seed.
- Compare floats with `pytest.approx(x)`, with `rel=` or `abs=` when the tolerance matters. Compare frames and series with `pd.testing.assert_series_equal`.
- For file-system tests, use `tmp_path` and `monkeypatch.setattr(module, "CONSTANT", tmp_path / ...)`. Use a fixture for the setup, named like `raw_dir` or `temp_dirs`.
- Several bad inputs go in `@pytest.mark.parametrize` with `ids=[...]`, each with a trailing comment naming the case, as in `tests/test_data.py`.
- Test functions have no type hints.

## Dependencies and scope

- Do not add a library when pandas, numpy or the standard library covers the need.
- Do not add a feature, flag or config option that was not requested.
- Do not reformat or rename code outside the requested change.
- Flag bugs you notice outside the task. Do not fix them unasked.
