# Used for synthetic price generator used by the test suite
import numpy as np
import pandas as pd

def make_prices(n: int = 2500, seed: int = 0, drift: float = 0.0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    vol = np.empty(n)
    vol[0] = 0.01

    for i in range(1, n):
        vol[i] = 0.9 * vol[i-1] + 0.1 * 0.008 + 0.0003 * abs(rng.standard_normal())

    log_ret = drift + vol * rng.standard_normal(n)
    close = 100 * np.exp(np.cumsum(log_ret))
    volume = rng.lognormal(mean=13, sigma=0.3, size=n)
    idx = pd.bdate_range("2012-01-02", periods=n, name="date")

    return pd.DataFrame({"close": close, "volume": volume}, index=idx)