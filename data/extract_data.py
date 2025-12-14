import yfinance as yf
import backtrader as bt
import pandas as pd

def import_MSFT(start='2011-01-01', end='2012-12-31'):
    df = yf.download('MSFT', start=start, end=end, auto_adjust=True)
    df.rename(columns={'Open':'open','High':'high','Low':'low','Close':'close',
                    'Adj Close':'adj_close','Volume':'volume'}, inplace=True)
    df.index.name = 'datetime'

    # Flatten columns if multi-index
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0].lower() for col in df.columns]  # Take first level and lowercase



    data = bt.feeds.PandasData(dataname=df)
    return data