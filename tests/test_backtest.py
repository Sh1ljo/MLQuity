# Tests for src/backtest.py
import numpy as np
import pandas as pd
import pytest

from src import backtest
from tests.fake_data import make_prices


def test_buy_and_hold_is_always_long():
    prices = make_prices(n=50)
    positions = backtest.buy_and_hold(prices)
    assert (positions == 1.0).all()
    assert positions.index.equals(prices.index)


def test_momentum_positions_are_zero_or_long():
    positions = backtest.momentum(make_prices(n=300), lookback=10)
    assert set(positions.unique()) <= {0.0, 1.0}


def test_momentum_flat_before_lookback():
    positions = backtest.momentum(make_prices(n=300), lookback=10)
    assert (positions.iloc[:10] == 0.0).all()


def test_momentum_signal_uses_only_past_data():
    idx = pd.bdate_range("2020-01-01", periods=25)
    up = pd.DataFrame({"close": np.linspace(100, 120, 25)}, index=idx)
    down = pd.DataFrame({"close": np.linspace(120, 100, 25)}, index=idx)
    assert backtest.momentum(up, lookback=5).iloc[-1] == 1.0
    assert backtest.momentum(down, lookback=5).iloc[-1] == 0.0


def test_buy_and_hold_matches_the_asset():
    prices = make_prices(n=500)
    returns = backtest.run_backtest(backtest.buy_and_hold(prices), prices)
    total = float((1 + returns).prod())
    held = prices["close"].iloc[-1] / prices["close"].iloc[0]
    assert total == pytest.approx(held, rel=1e-12)


def test_positions_shift_one_day_no_lookahead():
    # Only enter the market after seeing day 0, so days 1 and 2 are flat.
    idx = pd.bdate_range("2020-01-01", periods=4)
    prices = pd.DataFrame({"close": [100.0, 110.0, 99.0, 99.0]}, index=idx)
    positions = pd.Series([0.0, 1.0, 1.0, 1.0], index=idx)

    returns = backtest.run_backtest(positions, prices)

    # Day 1 holds positions[0] = 0 -> flat. Day 2 holds positions[1] = 1.
    assert returns.loc[idx[1]] == 0.0
    assert returns.loc[idx[2]] == pytest.approx(99.0 / 110.0 - 1)


def test_sharpe_zero_std_is_nan():
    flat = pd.Series([0.0, 0.0, 0.0])
    assert np.isnan(backtest.sharpe(flat))


def test_sharpe_of_known_series():
    returns = pd.Series([0.01, -0.01, 0.01, -0.01])
    expected = returns.mean() / returns.std() * np.sqrt(252)
    assert backtest.sharpe(returns) == pytest.approx(expected)


def test_summarize_counts_days():
    returns = pd.Series([0.1, -0.1])
    stats = backtest.summarize(returns)
    assert stats["n_days"] == 2
    assert stats["total_return"] == pytest.approx(0.99 - 1)


def test_momentum_signal_ignores_future_closes():
    prices = make_prices(n=600)
    cut = 400
    full = backtest.momentum(prices, lookback=252)

    # Signals computed on data cut at day `cut` match the full-data signals up to `cut`
    partial = backtest.momentum(prices.iloc[: cut + 1], lookback=252)
    pd.testing.assert_series_equal(full.iloc[: cut + 1], partial)

    # A wild close on day cut+1 must not change any signal up to `cut`
    changed = prices.copy()
    changed.iloc[cut + 1, changed.columns.get_loc("close")] = 1e6
    again = backtest.momentum(changed, lookback=252)
    pd.testing.assert_series_equal(full.iloc[: cut + 1], again.iloc[: cut + 1])


def test_zero_cost_is_the_default():
    prices = make_prices(n=300)
    positions = backtest.momentum(prices, lookback=10)
    default = backtest.run_backtest(positions, prices)
    zero = backtest.run_backtest(positions, prices, 0)
    pd.testing.assert_series_equal(default, zero)


def test_flat_position_pays_no_cost():
    prices = make_prices(n=50)
    positions = pd.Series(0.0, index=prices.index)
    returns = backtest.run_backtest(positions, prices, 50)
    assert (returns == 0.0).all()


def test_buy_and_hold_pays_one_entry_cost():
    prices = make_prices(n=50)
    positions = backtest.buy_and_hold(prices)
    cost = backtest.run_backtest(positions, prices, 0) - backtest.run_backtest(positions, prices, 10)

    # One entry at 10 bps, paid on the first day held (day 1), then nothing
    assert cost.iloc[0] == pytest.approx(0.001)
    assert cost.iloc[1:].abs().max() == pytest.approx(0.0, abs=1e-12)


def test_round_trip_pays_entry_and_exit():
    idx = pd.bdate_range("2020-01-01", periods=5)
    prices = pd.DataFrame({"close": [100.0, 101.0, 103.0, 102.0, 104.0]}, index=idx)
    positions = pd.Series([0.0, 1.0, 1.0, 0.0, 0.0], index=idx)  # held: 0, 0, 1, 1, 0

    cost = backtest.run_backtest(positions, prices, 0) - backtest.run_backtest(positions, prices, 10)

    assert cost.loc[idx[2]] == pytest.approx(0.001)  # entry
    assert cost.loc[idx[4]] == pytest.approx(0.001)  # exit
    assert cost.sum() == pytest.approx(0.002)


def test_cost_is_in_basis_points():
    prices = make_prices(n=50)
    positions = backtest.buy_and_hold(prices)
    cost = backtest.run_backtest(positions, prices, 0) - backtest.run_backtest(positions, prices, 5)
    assert cost.iloc[0] == pytest.approx(0.0005)  # 5 bps = 0.05%


def test_sharpe_is_scale_invariant():
    rng = np.random.default_rng(0)
    returns = pd.Series(rng.normal(0.0005, 0.01, 500))
    assert backtest.sharpe(3 * returns) == pytest.approx(backtest.sharpe(returns))


def test_sharpe_of_random_series_is_near_zero():
    rng = np.random.default_rng(0)
    returns = pd.Series(rng.normal(0, 0.01, 100_000))
    assert abs(backtest.sharpe(returns)) < 0.2  # about 4 standard errors


def test_sharpe_per_period_is_not_annualised():
    # Fails until sharpe() takes a `periods` argument (guide, Phase 0)
    returns = pd.Series([0.01, -0.01, 0.01, -0.01])
    per_period = backtest.sharpe(returns, periods=1)
    assert per_period == pytest.approx(returns.mean() / returns.std())
    assert backtest.sharpe(returns) == pytest.approx(per_period * np.sqrt(252))
