import pandas as pd
import pickle
import talib
import numpy as np
import statsmodels.api as sm


class Strategy:
    def __init__(self, close, high, low):
        self.days = close
        self.high = high
        self.low = low
        self.all_stocks = pd.DataFrame(close.columns[1:])
        self.trade_cal = list(close.date)
        self.res = {}
        self.hold_stocks = []
        self.buy_threshold = 0.7
        self.sell_threshold = -0.7

    def select_stock(self, anchor_date):
        results = pd.DataFrame()
        nd = self.days[self.days.date == anchor_date].index.to_list()[0]
        weeks = self.days[:nd]
        weeks.set_index('date', inplace=True)
        weeks = weeks.resample('W').last()
        for stock in self.all_stocks[0]:
            if stock not in self.days.columns:
                print(stock, 'has benn exited')
                break
            exo = pd.DataFrame()

            df = weeks[stock][-60:]
            df2 = self.days[stock][nd - 6:nd]
            if df.size == 0:
                results = results.append([False])
                continue
            for i in [5, 10, 20, 30, 60]:
                exo['ma' + str(i)] = talib.SMA(df, timeperiod=i)
            exo = exo.fillna(0)
            exo2 = df2.rolling(window=5).mean()
            if len(exo) < 2 or len(exo2) < 2:
                results = results.append([False])
                continue
            if (exo['ma5'].iloc[-1] > exo['ma10'].iloc[-1] > exo['ma20'].iloc[-1] >
                exo['ma30'].iloc[-1] > exo['ma60'].iloc[-1]) \
                    and not (exo['ma5'].iloc[-2] >= exo['ma10'].iloc[-2] >= exo['ma20'].iloc[-2] >=
                             exo['ma30'].iloc[-2] >= exo['ma60'].iloc[-2]) \
                    and (exo2.iloc[-2] > exo2.iloc[-1]):
                print(stock)
                results = results.append([True])
            else:
                results = results.append([False])

        results.index = self.all_stocks.index
        rets = self.all_stocks[results].dropna()
        print(anchor_date, 'has ', len(rets))
        return rets[0]

    def get_main_list(self, stocks=None):
        if stocks is None:
            stocks = self.all_stocks
        zbs = pd.DataFrame()
        for stock in stocks[0]:
            if stock.startswith('00') or stock.startswith('60'):
                zbs = zbs.append([True])
            else:
                zbs = zbs.append([False])
        zbs.index = stocks.index
        self.all_stocks = zbs

    def select_res(self):
        for d in self.trade_cal[487:-1]:  # start from 2011-07-01
            pre_d = self.trade_cal[self.days[self.days.date == d].index.to_list()[0] - 1]
            if d.month != pre_d.month:
                self.res[d] = list(self.select_stock(d))
            else:
                self.res[d] = []

    def generate_signal(self):
        anchor_date = 0
        for date in self.trade_cal[487:-1]:
            n = self.days[self.days.date == date].index.to_list()[0]
            if len(self.res[date]) > 0:
                anchor_date = date
                hold_stocks = self.res[date]
                self.res[date] = {'signal': 1, 'stocks': hold_stocks.copy()}
                print(date, 'buy: ', hold_stocks)
            else:
                self.res[date] = {'signal': 0, 'stocks': self.res[date]}
                sell = []
                buy = []
                ans = []
                for stock in self.hold_stocks.copy():
                    highs = self.high[stock][n - 18:n]
                    lows = self.low[stock][n - 18:n]
                    X = sm.add_constant(lows)
                    model = sm.OLS(highs, X)
                    beta = model.fit().params[1]
                    ans.append(beta)
                    # 计算r2
                    r2 = model.fit().rsquared

                    # 计算标准化的RSRS指标
                    # 计算均值序列
                    section = ans[-252:]
                    # 计算均值序列
                    mu = np.mean(section)
                    # 计算标准化RSRS指标序列
                    sigma = np.std(section)
                    zscore = (section[-1] - mu) / sigma
                    # 计算右偏RSRS标准分
                    zscore_rightdev = zscore * beta * r2

                    # 如果上一时间点的RSRS斜率大于买入阈值, 则全仓买入
                    if zscore_rightdev > self.buy_threshold and stock not in self.hold_stocks:
                        # 满足条件运行交易
                        buy += [stock]
                    # 如果上一时间点的RSRS斜率小于卖出阈值, 则空仓卖出
                    elif (zscore_rightdev < self.sell_threshold) and stock in self.hold_stocks:
                        sell += [stock]
                    pct = (self.days[stock][self.days.date == date].iloc[0] -
                           self.days[stock][self.days.date == anchor_date].iloc[0]) / \
                          self.days[stock][self.days.date == anchor_date].iloc[0]
                    if pct <= -0.1 or pct > 0.15 or date.month != self.trade_cal[
                        self.days[self.days.date == date].index.to_list()[0] + 1].month:
                        sell += [stock]
                        self.hold_stocks.remove(stock)
                if len(sell) > 0:
                    self.res[date] = {'signal': -1, 'stocks': sell}
                    print(date, 'sell: ', sell)


if __name__ == '__main__':
    closes = pd.read_csv('close.csv')
    closes.date = pd.to_datetime(closes.date)
    highs = pd.read_csv('high.csv')
    lows = pd.read_csv('low.csv')

    my_strategy = Strategy(closes, highs, lows)
    # my_strategy.get_main_list()
    my_strategy.select_res()
    my_strategy.generate_signal()
    res = my_strategy.res

    with open('lossstop.pkl', 'wb') as f:
        pickle.dump(res, f, 4)
