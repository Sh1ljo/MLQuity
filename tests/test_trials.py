# Tests for src/trials.py
import pandas as pd
import pytest

from src import trials
from src.backtest import summarize


@pytest.fixture
def temp_dirs(tmp_path, monkeypatch):
    monkeypatch.setattr(trials, "TRIALS_CSV", tmp_path / "trials.csv")
    monkeypatch.setattr(trials, "RETURNS_DIR", tmp_path / "returns")


def test_first_trial_gets_id_1(temp_dirs):
    trial_id = trials.log_trial({"strategy": "buy_and_hold"}, pd.Series([0.01, 0.02]))
    assert trial_id == 1
    assert trials.TRIALS_CSV.exists()


def test_ids_increment_and_rows_append(temp_dirs):
    returns = pd.Series([0.01, -0.02, 0.03])
    trials.log_trial({"strategy": "a"}, returns)
    trials.log_trial({"strategy": "b"}, returns)

    log = pd.read_csv(trials.TRIALS_CSV)
    assert list(log["trial_id"]) == [1, 2]
    assert list(log["config"]) == ["strategy=a", "strategy=b"]


def test_row_stats_match_returns(temp_dirs):
    returns = pd.Series([0.01, -0.02, 0.03])
    trials.log_trial({"strategy": "buy_and_hold", "ticker": "SPY"}, returns)

    log = pd.read_csv(trials.TRIALS_CSV)
    assert log["n_days"].iloc[0] == 3
    assert log["total_return"].iloc[0] == pytest.approx((1 + returns).prod() - 1)
    assert log["sharpe"].iloc[0] == pytest.approx(summarize(returns)["sharpe"])


def test_returns_saved_per_trial(temp_dirs):
    returns = pd.Series([0.01, -0.02, 0.03], name="return")
    trials.log_trial({}, returns)

    saved = pd.read_csv(trials.RETURNS_DIR / "trial_0001.csv")
    assert list(saved["return"]) == pytest.approx(list(returns))
    assert pd.read_csv(trials.TRIALS_CSV)["returns_file"].iloc[0] == "trial_0001.csv"
