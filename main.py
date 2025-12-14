from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

# Import the backtrader platform, data and trade strategy
import backtrader as bt
import backtrader.strategies as btstrats
import backtrader.analyzers as btanalyzers

# Import common libraries for data and plot handling
import datetime
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
import argparse

# Import custom modules for data and strategy
from data import extract_data
from tradalgo import simple_algo

def walk_forward_cv():
    #Initialise results DataFrame for starting and ending values for each walking CV fold
    res_df = pd.DataFrame(columns=['Date','Open', 'Close', 'Sharpe Ratio'])
    res_df.set_index('Date', inplace=True)

    #Set start and end dates
    latest = datetime.date.today() - datetime.timedelta(days=1)
    earliest = datetime.date(2015, 1, 1)
    period = datetime.timedelta(days = 5*365)

    #Extract data from yfinance by calling from extract_data module
    data = extract_data.import_AUDUSD(start=earliest, end=latest)

    curr = earliest
    fold_id = 0
    index = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    os.mkdir('results/' + index)


    #Run walking cross validation (365 day steps, 5*365 day backtesting periods)
    while curr + period < latest:
        curr_data = data.loc[curr:curr + period]
        start_value, end_value, sharpe_ratio = runstrat(curr_data, fold_id, index)

        # Store results in Dataframe
        new_row = pd.Series(
            {"Open": start_value, "Close": end_value, "Sharpe Ratio": sharpe_ratio}
        )
        res_df.loc[curr] = new_row
        curr += datetime.timedelta(days = 365)
        fold_id += 1

    #Save results

    res_df.to_csv('results/' + index + '/results.csv')


def runstrat(data_df, fold_id, index):
    args = parse_args()

    # Create a cerebro entity
    cerebro = bt.Cerebro(stdstats=False)

    # Add a strategy
    #cerebro.addstrategy(simple_algo.SmaCross)
    cerebro.addstrategy(btstrats.SMA_CrossOver)

    # Analyzer
    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='sharpe')

    # Simulate the header row isn't there if noheaders requested
    skiprows = 1 if args.noheaders else 0
    header = None if args.noheaders else 0

    # Create a Data Feed
    data = bt.feeds.PandasData(dataname=data_df)

    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Set a fixed commission
    cerebro.broker.setcommission(
        commission=0.001,  # 0.1% per trade
        margin=None,
        mult=1.0,
        name=None
    )
    cerebro.broker.set_slippage_perc(perc=0.0001) # 1 pip

    # Run trading algorithm fold
    open = cerebro.broker.getvalue()
    cerebro_run = cerebro.run()
    sharpe_ratio =  cerebro_run[0].analyzers.sharpe.get_analysis()['sharperatio']
    close = cerebro.broker.getvalue()

    # Save plot figure
    figs = cerebro.plot(iplot=False)
    fig = figs[0][0]

    fig.savefig(f"results/{index}/fold_{fold_id}.png",
                dpi=300,
                bbox_inches="tight")

    plt.close(fig)

    return (open, close, sharpe_ratio)

def parse_args():
    parser = argparse.ArgumentParser(
        description='Pandas test script')

    parser.add_argument('--noheaders', action='store_true', default=False,
                        required=False,
                        help='Do not use header rows')

    parser.add_argument('--noprint', action='store_true', default=False,
                        help='Print the dataframe')

    return parser.parse_args()


if __name__ == '__main__':
    walk_forward_cv()