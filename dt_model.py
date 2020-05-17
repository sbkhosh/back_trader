#!/usr/bin/python3

import backtrader as bt
import pandas as pd

from dt_help import Helper

class SmaCross(bt.SignalStrategy):
    def __init__(self):
        sma1 = bt.ind.SMA(period=10)
        sma2 = bt.ind.SMA(period=30)
        crossover = bt.ind.CrossOver(sma1, sma2)
        self.signal_add(bt.SIGNAL_LONG, crossover)
        
    def exec_model(data,ticker,dir_out):
        cerebro = bt.Cerebro()
        cerebro.addstrategy(SmaCross)
        cerebro.adddata(data)
        cerebro.run()
        cerebro.plot()
