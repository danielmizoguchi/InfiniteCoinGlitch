from datetime import datetime
import backtrader as bt

class SmaCross(bt.Strategy):
    # list of parameters which are configurable for the strategy
    params = dict(
        pfast=10,  # period for the fast moving average
        pslow=50   # period for the slow moving average
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        #print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Declare opening of CV fold
        self.log('\nSTART, %.2f' % self.data.close[0])
        # Initialising long and short term moving averages
        sma1 = bt.ind.SMA(period=self.p.pfast)  # fast moving average
        sma2 = bt.ind.SMA(period=self.p.pslow)  # slow moving average
        self.crossover = bt.ind.CrossOver(sma1, sma2)  # crossover signal


    def next(self):
        if not self.position:  # not in the market
            if self.crossover > 0:  # if fast crosses slow to the upside
                self.buy(size=100)  # enter long
                self.log('BUY CREATE, %.2f' % self.data.close[0])

        elif self.crossover < 0:  # in the market & cross to the downside
            self.log('CLOSE CREATE, %.2f' % self.data.close[0])
            self.close()  # close long position