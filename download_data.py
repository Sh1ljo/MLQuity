import pathlib

import pandas as pd
import requests

# Settings
TICKERS = ["SPY"]            # what to download, e.g. ["SPY", "AAPL", "MSFT"]
START_DATE = "2020-01-01"    # first day
END_DATE = "2026-10-01"      # last day

KEY_FILE = pathlib.Path("tiingo_key.txt")
RAW_DIR = pathlib.Path("data/raw")
API_URL = "https://api.tiingo.com/tiingo/daily/{ticker}/prices"


def read_api_key() -> str:
    if not KEY_FILE.exists():
        raise FileNotFoundError(
            f"{KEY_FILE} not found. Create it and put your Tiingo API key inside."
        )

    key = KEY_FILE.read_text(encoding="utf-8-sig").strip()
    if not key or key == "PUT-YOUR-KEY-HERE":
        raise ValueError(
            f"Open {KEY_FILE} and replace PUT-YOUR-KEY-HERE with your real Tiingo API key."
        )
    return key


def download_ticker(ticker: str, api_key: str) -> pd.DataFrame:

    response = requests.get(
        API_URL.format(ticker=ticker),
        params={"startDate": START_DATE, "endDate": END_DATE},
        headers={"Authorization": f"Token {api_key}"},
        timeout=30,
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"Tiingo answered {response.status_code} for {ticker}: {response.text}\n"
            "Check your API key and the ticker symbol."
        )

    rows = response.json()
    if not isinstance(rows, list) or len(rows) == 0:
        raise RuntimeError(f"Tiingo returned no price rows for {ticker}: {rows}")

    df = pd.DataFrame(rows)
    # Keep only what we need: the adjusted close and the split-adjusted volume.
    df = df[["date", "adjClose", "adjVolume"]]
    df = df.rename(columns={"adjClose": "close", "adjVolume": "volume"})
    # Tiingo dates look like "2026-10-13T00:00:00.000Z"; keep only the day
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    return df


def main() -> None:
    api_key = read_api_key()
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for ticker in TICKERS:
        ticker = ticker.upper()
        df = download_ticker(ticker, api_key)
        out_path = RAW_DIR / f"{ticker}.csv"
        df.to_csv(out_path, index=False)
        print(
            f"{ticker}: {len(df)} rows, {df['date'].iloc[0]} to {df['date'].iloc[-1]}"
            f"  ->  {out_path}"
        )


if __name__ == "__main__":
    main()
