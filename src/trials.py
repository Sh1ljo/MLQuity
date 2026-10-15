# Logs every trial in trials.csv and saves each trial's daily returns
import pathlib

import pandas as pd

from src.backtest import summarize

ROOT = pathlib.Path(__file__).resolve().parents[1]
RETURNS_DIR = ROOT / "data" / "processed" / "trials"
TRIALS_CSV = RETURNS_DIR / "trials.csv"

def next_trial_id() -> int:
    if not TRIALS_CSV.exists() or TRIALS_CSV.stat().st_size == 0:
        return 1
    return int(pd.read_csv(TRIALS_CSV)["trial_id"].max()) + 1


def log_trial(config: dict, returns: pd.Series) -> int:
    RETURNS_DIR.mkdir(parents=True, exist_ok=True)

    trial_id = next_trial_id()
    returns_path = RETURNS_DIR / f"trial_{trial_id:04d}.csv"
    returns.rename("return").to_csv(returns_path)

    row = {
        "trial_id": trial_id,
        "config": ", ".join(f"{key}={value}" for key, value in config.items()),
        **summarize(returns),
        "returns_file": returns_path.name,
    }
    pd.DataFrame([row]).to_csv(
        TRIALS_CSV, mode="a", header=not TRIALS_CSV.exists(), index=False
    )
    return trial_id
