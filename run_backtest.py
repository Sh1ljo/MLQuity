# Runs the Phase 0 baseline strategies end to end and logs each as a trial
from src import backtest, data, trials


def main() -> None:
    ticker = "SPY"
    prices = data.load_prices(ticker)

    strategies = {
        "buy_and_hold": backtest.buy_and_hold(prices),
        "momentum_252d": backtest.momentum(prices),
    }

    for name, positions in strategies.items():
        returns = backtest.run_backtest(positions, prices)
        stats = backtest.summarize(returns)

        trial_id = trials.log_trial({"strategy": name, "ticker": ticker}, returns)

        first, last = returns.index[0].date(), returns.index[-1].date()
        print(f"{name} {ticker}, {first} to {last} ({stats['n_days']} days)")
        print(f"Total return: {stats['total_return']:.4%}")
        print(f"Sharpe:       {stats['sharpe']:.3f}")
        print(f"Logged trial {trial_id} -> "
              f"{trials.TRIALS_CSV.relative_to(trials.ROOT).as_posix()}")
        print()


if __name__ == "__main__":
    main()
