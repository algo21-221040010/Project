'''
根据因子信号进行交易


Functions 
- backtest 进行回测
    - 需要调用 Trade 类

Class
- Trade  根据策略信号 进行 买buy()、卖sell()、更新持仓净值hold() 等操作


Return
- trade_data [dict]  {date: {
                            'date','all_position_value', 'cash',
                            'value', 'signal', 'cost',
                            '','r_price','position', 'position_value'}
                     }
'''
from copyreg import pickle
import pandas as pd
import datetime


def backtest(trade_dt, trade_price, signal):
    trade_dict = {}
    # 调用 Trade 类，进行模拟交易
    trade = Trade()  
    for date in trade_dt:
        trade.update(date, price=trade_price[date], signal=signal[date])
        trade_dict[date] = trade.trade()
    
    trade_data = pd.DataFrame.from_dict(trade_dict, 'index')  # 获得交易持仓净值数据
    trade_data.index = pd.to_datetime(trade_data.index)
    # 回测指标分析
    analyse = Evaluate(trade_data)
    evaluate_data = analyse.evaluate()
    return trade_data, evaluate_data


class Trade():
    def __init__(self, allocation=10000):
        self.date_time = None  # signalData.date
        self.trade_price = None
        self.signal = None

        # 参数：初始资金 1
        self.allocation = allocation
        self.commission = 0.0002

        # 交易数据
        self.cash = self.allocation  # 初始化现金为上期现金值
        self.value = allocation
        self.position = 0
        self.position_value = 0

    def get_trade_position(self): 
        position = (self.pre_value) // ((1 + self.commission) * self.trade_price)
        trade_position = position - self.pre_position
        return trade_position

    def buy(self):
        long_position = self.cash // ((1 + self.commission) * self.trade_price) # 增加的头寸
        long_position_value = long_position * self.trade_price
        
        self.position = long_position
        self.position_value = self.position * self.trade_price # 所有头寸乘今天的价格（pre值用的是昨天的价格
        self.cost = self.commission * long_position_value

        self.cash = self.cash - self.cost - long_position_value
        self.value = self.cash + self.position_value
        return self.position_value

    def sell(self):
        short_position = self.position # 负值，表示降低/做空的头寸
        short_position_value = short_position * self.trade_price # 负值， 降低的头寸价值

        self.cost = self.commission * abs(short_position_value)
        self.cash += short_position_value
        
        self.position = 0
        self.position_value = self.position * self.trade_price # 今天价格算的 持仓价值
        self.value = self.cash + self.position_value
        # return self.position_value

    def hold(self):
        self.get_position_value()
        # cash 不变
        self.value = self.cash + self.position_value

    def get_position_value(self):
        self.position_value = self.position * self.trade_price
        return self.position_value

    def update(self, date_time, price, signal):
        self.date_time = date_time
        # self.weight = weight
        self.trade_price = price  
        self.signal = signal # 0


    def trade(self, show_info=False):
        """ 开始交易"""
        if self.signal > 0:
            if self.cash > 0:
                self.buy()
        elif self.signal < 0:  
            if self.position > 0:         
                self.sell()
        elif self.signal == 0:
            self.hold()
        else:
            raise ValueError('Invalid "signal" value!')
        self.value = self.position_value + self.cash
    
        trade_info = self.get_trade_data()
        if show_info:
            self.show_trading_info()  # 打印交易详情
        return trade_info

    # 获取 并 存储
    def get_trade_data(self):
        '''
        Return
            [dict]  {date: {'date_time','position_value', 'cash', 'weight', 'signal',
                            
                            }
        '''
        param_list = ['value', 'trade_price', 'position_value', 'cash', 'signal']
        value = {name: getattr(self, name) for name in param_list}
        return value

    def show_trading_info(self):
        if self.signal > 0:
            print(f'{self.date_time} 换仓，买入，'
                  f'持仓价值 {self.position_value:.2f}，剩余 {self.cash:.2f} 现金')
        else:
            print(f'{self.date_time} 无操作，当前持仓价值 {self.position_value:.2f}，总资产 {self.value:.2f}')



if __name__ == '__main__':
    # 数据导入国内股债收盘价
    from Evaluate import *
    from Pictures import Pictures 
    from TWAP import Twap

    import pickle
    def load_obj(name): 
        with open(name, 'rb') as f: 
            return pickle.load(f)
    signal = load_obj(r'data\signal.pkl')
    signal_df = pd.DataFrame.from_dict(signal, 'index')
    signal_df.index = pd.to_datetime(signal_df.index)
    signal = signal_df.to_dict().get(0)
    # print(signal_df)
    # keys = []
    # for key, value in signal:
    #     keys.append(pd.to_datetime(key)
    # signal = dict(zip([],[](]))
    # print(signal)
    
    trade_data = pd.read_csv(r'data\202202bidask.csv', index_col=1)
    print(trade_data)
    trade_data.index = pd.to_datetime(trade_data.index)
    
    trade_dt = list(trade_data.index)
    trade_price = trade_data['BuyPrice01'].to_dict()

    trade_dict = {}
    # 调用 Trade 类，进行模拟交易
    trade = Trade()  
    for date in trade_dt:
        trade.update(date, price=trade_price[date], signal=signal[date])
        trade_dict[date] = trade.trade()
    
    trade_data = pd.DataFrame.from_dict(trade_dict, 'index')  # 获得交易持仓净值数据
    trade_data.index = pd.to_datetime(trade_data.index)
    # 回测指标分析
    analyse = Evaluate(trade_data)
    evaluate_data = analyse.evaluate()

    p = Pictures(trade_data)
    print(type(p).__name__)
    # Pictures.draw_value_ret(trade_data)

