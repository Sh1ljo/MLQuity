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


def test_sharpe_zero_std_is_zero():
    flat = pd.Series([0.0, 0.0, 0.0])
    assert backtest.sharpe(flat) == 0.0


def test_sharpe_of_known_series():
    returns = pd.Series([0.01, -0.01, 0.01, -0.01])
    expected = returns.mean() / returns.std() * np.sqrt(252)
    assert backtest.sharpe(returns) == pytest.approx(expected)


def test_summarize_counts_days():
    returns = pd.Series([0.1, -0.1])
    stats = backtest.summarize(returns)
    assert stats["n_days"] == 2
    assert stats["total_return"] == pytest.approx(0.99 - 1)
