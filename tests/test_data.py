# Tests for src/data.py
import pandas as pd
import pytest

from src import data


@pytest.fixture
def raw_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(data, "RAW_DIR", tmp_path)
    return tmp_path


def write_spy(raw_dir, rows):
    pd.DataFrame(rows, columns=["date", "close", "volume"]).to_csv(
        raw_dir / "SPY.csv", index=False
    )


def test_clean_file_loads_sorted_and_unique(raw_dir):
    write_spy(raw_dir, [
        ("2020-01-03", 101.0, 1000),
        ("2020-01-02", 100.0, 1000),
        ("2020-01-06", 102.0, 1000),
    ])
    df = data.load_prices("SPY")
    assert df.index.is_monotonic_increasing
    assert df.index.is_unique
    assert len(df) == 3


@pytest.mark.parametrize("rows", [
    [("2020-01-02", 100, 1), ("2020-01-02", 101, 1)],   # duplicate date
    [("2020-01-02", 100, 1), ("2020-01-03", None, 1)],  # missing close
    [("2020-01-02", 100, 1), ("2020-01-03", 0, 1)],     # zero close
    [("2020-01-02", 100, 1), ("2020-01-03", -5, 1)],    # negative close
    [("2020-01-02", 100, 1), ("2020-01-03", 160, 1)],   # 60% one-day jump
], ids=["duplicate", "missing", "zero", "negative", "jump"])
def test_bad_data_raises(raw_dir, rows):
    write_spy(raw_dir, rows)
    with pytest.raises(ValueError):
        data.load_prices("SPY")
