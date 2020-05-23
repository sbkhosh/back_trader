#!/usr/bin/python3

import backtrader as bt
import backtrader.indicators as btind
import pandas as pd

from dt_help import Helper

class SmaCross(bt.SignalStrategy):
    def __init__(self):
        sma1 = bt.ind.SMA(period=10)
        sma2 = bt.ind.SMA(period=30)
        crossover = bt.ind.CrossOver(sma1, sma2)
        self.signal_add(bt.SIGNAL_LONG, crossover)

    def exec_model(data,cash):
        cerebro = bt.Cerebro()
        cerebro.adddata(data)
        cerebro.broker.setcash(cash)
        cerebro.addstrategy(SmaCross)
        print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
        cerebro.run()
        print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
        cerebro.plot()
        
class LogPrice(bt.Strategy):
    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        
    def log_price(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log_price('Close, %.2f' % self.dataclose[0])

    def exec_model(data,cash):
        cerebro = bt.Cerebro()
        cerebro.adddata(data)
        cerebro.broker.setcash(cash)
        cerebro.addstrategy(LogPrice)
        print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
        cerebro.run()
        print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
        cerebro.plot()

class SmaEma(bt.Strategy):
    def __init__(self):
        sma1 = btind.SimpleMovingAverage(self.data)
        ema1 = btind.ExponentialMovingAverage()

        close_over_sma = self.data.close > sma1
        close_over_ema = self.data.close > ema1
        sma_ema_diff = sma1 - ema1

        self.buy_sig = bt.And(close_over_sma, close_over_ema, sma_ema_diff > 0)

    def next(self):
        if self.buy_sig:
            self.buy()

    def exec_model(data,cash):
        cerebro = bt.Cerebro()
        cerebro.adddata(data)
        cerebro.broker.setcash(cash)
        cerebro.addstrategy(SmaEma)
        print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
        cerebro.run()
        print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
        cerebro.plot()
        
class BollStrat(bt.Strategy):
    '''
    simple mean reversion bollinger band strategy.

    entry critria:
        - long:
            - price closes below the lower band
            - stop order entry when price crosses back above the lower band
        - short:
            - price closes above the upper band
            - stop order entry when price crosses back below the upper band
    exit critria
        - long/short: price touching the median line
    '''
    params = (
        ("period", 40),
        ("devfactor", 2),
        ("size", 20),
        ("debug", False)
        )

    def __init__(self):
        self.boll = bt.indicators.BollingerBands(period=self.p.period, devfactor=self.p.devfactor)
        #self.sx = bt.indicators.CrossDown(self.data.close, self.boll.lines.top)
        #self.lx = bt.indicators.CrossUp(self.data.close, self.boll.lines.bot)

    def next(self):
        orders = self.broker.get_orders_open()

        # Cancel open orders so we can track the median line
        if(orders):
            for order in orders:
                self.broker.cancel(order)

        if(not self.position):
            if(self.data.close > self.boll.lines.top):
                self.sell(exectype=bt.Order.Stop, price=self.boll.lines.top[0], size=self.p.size)
            if(self.data.close < self.boll.lines.bot):
                self.buy(exectype=bt.Order.Stop, price=self.boll.lines.bot[0], size=self.p.size)
        else:
            if(self.position.size > 0):
                self.sell(exectype=bt.Order.Limit, price=self.boll.lines.mid[0], size=self.p.size)
            else:
                self.buy(exectype=bt.Order.Limit, price=self.boll.lines.mid[0], size=self.p.size)

        if(self.p.debug):
            print('---------------------------- NEXT ----------------------------------')
            print("1: Data Name:                            {}".format(data._name))
            print("2: Bar Num:                              {}".format(len(data)))
            print("3: Current date:                         {}".format(data.datetime.datetime()))
            print('4: Open:                                 {}'.format(data.open[0]))
            print('5: High:                                 {}'.format(data.high[0]))
            print('6: Low:                                  {}'.format(data.low[0]))
            print('7: Close:                                {}'.format(data.close[0]))
            print('8: Volume:                               {}'.format(data.volume[0]))
            print('9: Position Size:                        {}'.format(self.position.size))
            print('--------------------------------------------------------------------')

    def notify_trade(self,trade):
        if(trade.isclosed):
            dt = self.data.datetime.date()

            print('---------------------------- TRADE ---------------------------------')
            print("1: Data Name:                            {}".format(trade.data._name))
            print("2: Bar Num:                              {}".format(len(trade.data)))
            print("3: Current date:                         {}".format(dt))
            print('4: Status:                               Trade Complete')
            print('5: Ref:                                  {}'.format(trade.ref))
            print('6: PnL:                                  {}'.format(round(trade.pnl,2)))
            print('--------------------------------------------------------------------')

    def exec_model(data,cash):
        cerebro = bt.Cerebro()
        cerebro.adddata(data)
        cerebro.broker.setcash(cash)
        cerebro.addstrategy(BollStrat)
        print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
        cerebro.run()
        print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
        cerebro.plot(style='candlestick')

        
