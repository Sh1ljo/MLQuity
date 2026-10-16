# Turns daily positions into strategy returns, plus simple summary stats
import numpy as np
import pandas as pd


# Position for buy-hold : Fully long every day
def buy_and_hold(prices: pd.DataFrame) -> pd.Series:
    return pd.Series(1.0, index=prices.index)


# Position for momentum : Long if price rose over the past `lookback` days, else flat
def momentum(prices: pd.DataFrame, lookback: int = 252) -> pd.Series:
    close = prices["close"]
    past_ret = close.pct_change(lookback)
    return (past_ret > 0).astype(float)


def run_backtest(positions, prices, cost_bps: float = 0.0) -> pd.Series:
    close = prices["close"]
    asset_ret = close.pct_change()
    held = positions.shift(1).fillna(0)
    turnover = (held - held.shift(1, fill_value=0)).abs()  # first entry counts as a trade
    cost = cost_bps / 10000 * turnover
    return (held * asset_ret - cost).dropna()

# Sharpe ratio over period
def sharpe(returns: pd.Series, periods: int = 252) -> float:
    mean = returns.mean()
    std = returns.std()
    if std == 0 or np.isnan(std):
        return np.nan
    sr_pp = mean / std
    return float(sr_pp * np.sqrt(periods))


# Headline numbers for one backtest
def summarize(returns: pd.Series) -> dict:
    total = float((1 + returns).prod() - 1)
    return {
        "n_days": int(len(returns)),
        "total_return": total,
        "sharpe": sharpe(returns),
    }
