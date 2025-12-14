from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

# Import the backtrader platform, data and trade strategy
import backtrader as bt
import datetime
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

from data import extract_data
from tradalgo import simple_algo
import argparse

def walk_forward_cv():
    #Initialise folder storage index
    index = datetime.date.strftime(datetime.datetime.now(), format='%Y-%m-%d-%H:%M')
    os.mkdir('results/' + index)

    #Initialise results DataFrame for starting and ending values for each walking CV fold
    res_df = pd.DataFrame(columns=['Date','Open', 'Close'])
    res_df.set_index('Date', inplace=True)

    #Set start and end dates
    latest = datetime.date.today() - datetime.timedelta(days=1)
    earliest = datetime.date(2015, 1, 1)
    period = datetime.timedelta(days = 5*365)

    #Extract data from yfinance by calling from extract_data module
    data = extract_data.import_AUDUSD(start=earliest, end=latest)

    curr = earliest
    fold_id = 0

    #Run walking cross validation (365 day steps, 5*365 day backtesting periods)
    while curr + period < latest:
        curr_data = data.loc[curr:curr + period]
        start_value, end_value = runstrat(curr_data, fold_id, index)

        # Store results in Dataframe
        new_row = pd.Series(
            {"Open": start_value, "Close": end_value}
        )
        res_df.loc[curr] = new_row
        curr += datetime.timedelta(days = 365)
        fold_id += 1

    #Save results

    res_df.to_csv('results/' + index + '/results_.csv')


def runstrat(data_df, fold_id, index):
    args = parse_args()

    # Create a cerebro entity
    cerebro = bt.Cerebro(stdstats=False)

    # Add a strategy
    cerebro.addstrategy(simple_algo.SmaCross)

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

    open = cerebro.broker.getvalue()
    cerebro.run()
    close = cerebro.broker.getvalue()

    figs = cerebro.plot(iplot=False)
    fig = figs[0][0]

    fig.savefig(f"results/{index}/fold_{fold_id}.png",
                dpi=300,
                bbox_inches="tight")

    plt.close(fig)

    return (open, close)

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