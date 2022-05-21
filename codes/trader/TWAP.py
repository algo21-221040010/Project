from time import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from OrderBook import OrderBook, get_orderbook_data

from Trade import Trade


class Twap(Trade):
    """
    Twap 算法实现了在设定的交易时间段内，完成设定的下单手数。
    """
    def __init__(self, symbol='IF2206', account=None, allocation= 1000000):
        """创建 Twap 实例
        
        Args:
            symbol (str): 拟下单的合约symbol, 例如 "IF2206"
            account: [可选]指定发送下单指令的账户实例, 多账户模式下，该参数必须指定
        """
        self._account = account
        self._symbol = symbol
        self.date_time = None
        
        # twap 交易的参数
        self.span = None
        self.per_volume = None

        # orderbook 数据
        orderbook_data, time_list = get_orderbook_data()
        self.time_list = time_list
        self.orderbook = OrderBook(data=orderbook_data, symbol=symbol)  # TODO 从数据库获取数据

        self.trade_info = {}  # 所有的 trade 信息数据
        
        # 参数：初始资金 1
        self.allocation = allocation
        self.commission = 0.0002
        self.cash = allocation  # 初始化现金为上期现金值
        self.value = allocation
        self.position_value = 0
        self.position = 0
        self.signal = None
    
    def set_span_and_per_volume(self, span:int, per_volume:int):
        """ 设置 twap 的交易参数

        Args:
            span (int): 算法执行交易的总时长，以秒为单位
            per_volume (int):  每次下单的手数
        """
        self.span = span
        self.per_volume = per_volume

    def get_trade_ts(self, start_time, trade_num):
        """获取每次交易的时间戳

        Args:
            start_time (datetime): 本次交易开始时间点

        Returns:
            list: 本次twap拆单的所有交易时间点
        """
        each_interval = self.span / trade_num
        trade_time = []
        for i in range(self.trade_num):
            end_time = start_time + timedelta(seconds=each_interval)
            time_inner = [t for t in self.time_list if end_time > t > start_time ]
            start_time = end_time
            trade_time.append(time_inner[0]) 
        return trade_time

    def buy(self, datetime, position):
        price_vol = self.orderbook.get_price_volume(datetime=datetime, 
                                    direction='sell', trade_volume=position)
        price_vol_data = pd.DataFrame.from_dict(price_vol) #.sum()
        
        self.position += position 
        self.position_value += np.sum(price_vol_data.loc['price'] * price_vol_data.loc['volume'])
        self.cost = self.commission * self.position_value
        self.cash = self.cash - self.cost - self.position_value
        self.value = self.cash + self.position_value

        avg_price =  self.position_value / position
        
        trade_info = {'direction':'buy', 'avg_price':avg_price, 'volume':position, 'trade_detail':price_vol}
        return trade_info

    def sell(self, datetime, position):
        # 按 tick sell
        price_vol = self.orderbook.get_price_volume(datetime=datetime, 
                                    direction='buy', trade_volume=position)
        price_vol = pd.DataFrame.from_dict(price_vol) #.sum()

        # 更新持仓数据
        self.position -= position
        assert self.position >= 0, 'cannot have negative position!'
        short_position_value = np.sum(price_vol.loc['price'] * price_vol.loc['volume'])
        self.position_value -= short_position_value
        self.cost = self.commission * abs(short_position_value)
        self.cash += short_position_value - self.cost
        self.position = 0
        self.position_value = 0 
        self.value = self.cash + self.position_value
        
        avg_price =  self.position_value / position

        trade_info = {'direction':'sell', 'avg_price':avg_price, 'volume':position, 'trade_detail':price_vol}
        return trade_info

    def hold(self, datetime):
        mid_price = self.orderbook.get_mid_price(datetime=datetime)
        self.position_value = mid_price * self.position

    def trade(self, signal, total_volume, start_time):
        """进行交易

        Args:
            direction (str): 交易方向，'buy' or 'sell'
            total_volume (int): 下单的总手数
            start_time (datetime): 本次交易开始时间点
            span (int): 算法执行交易的总时长，以秒为单位
            per_volume (int): 每次下单的手数

        Returns:
            dict: 交易信息
        """
        trade_num = total_volume // self.per_volume  # 计算下单次数
        trade_time = self.get_trade_ts(start_time, trade_num)
        if signal > 0:
            for t in trade_time:
                self.trade_info[t] = self.buy(self.per_volume)
                self.trade_info[t]['position_value'] = self.position_value
                # TODO 存入数据库

        elif signal < 0:
            for t in trade_time:
                self.trade_info[t] = self.sell(self.per_volume)
                # TODO 存入数据库
        
        else:
            self.hold()

        return self.trade_info

    
if __name__ == '__main__':
    # 数据导入国内股债收盘价
    from Evaluate import *
    from Pictures import Pictures 

    import pickle


    def load_obj(name): 
        with open(name, 'rb') as f: 
            return pickle.load(f)
    signal = load_obj(r'data\signal.pkl')

    # orderbook 数据
    orderbook_data, time_list = get_orderbook_data()
    orderbook = OrderBook(data=orderbook_data)

    trade_dict = {}
    price = 0 # TODO 就是 bid ask price
    # 调用 Trade 类，进行模拟交易
    twap = Twap()  
    for dt in time_list:
        # TODO
        trade_dict[dt] = twap.trade()
    
    trade_data = pd.DataFrame.from_dict(trade_dict, 'index')  # 获得交易持仓净值数据
    trade_data.index = pd.to_datetime(trade_data.index)
    
    # 回测指标分析
    analyse = Evaluate(trade_data)
    evaluate_data = analyse.evaluate()

    print(evaluate_data)
    p = Pictures(trade_data)
    p.draw()


    