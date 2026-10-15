# Loads prices from csv
import pathlib
import pandas as pd

RAW_DIR = pathlib.Path(__file__).resolve().parents[1] / "data" / "raw"


def load_prices(ticker: str = "SPY") -> pd.DataFrame:
    path = RAW_DIR / f"{ticker}.csv"
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    df = pd.read_csv(path, parse_dates=["date"]).set_index("date").sort_index()

    # Check the quality of data
    dupes = df.index[df.index.duplicated()]
    if not dupes.empty:
        raise ValueError(f"Duplicate dates: {list(dupes)}")
    if df["close"].isna().any():
        missing = df.index[df["close"].isna()]
        raise ValueError(f"Missing close on: {list(missing)}")

    return df
