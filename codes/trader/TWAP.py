from time import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
# from codes.backtest.Trade import Stock
from OrderBook import OrderBook, get_orderbook_data


class Twap():
    """
    Twap 算法实现了在设定的交易时间段内，完成设定的下单手数。
    """
    def __init__(self, symbol='IF2206', account = None):
        """创建 Twap 实例
        
        Args:
            symbol (str): 拟下单的合约symbol, 例如 "IF2206"
            account: [可选]指定发送下单指令的账户实例, 多账户模式下，该参数必须指定
        """
        self._account = account
        self._symbol = symbol
        # orderbook 数据
        orderbook_data, time_list = get_orderbook_data()
        self.time_list = time_list
        self.orderbook = OrderBook(data=orderbook_data, symbol=symbol)  # TODO 从数据库获取数据
        self.trade_info = {}  # 所有的 trade 信息数据
        self.position_value = 0
        self.position = 0
    
    def get_trade_ts(self, start_time, span:int, trade_num:int):
        """获取每次交易的时间戳

        Args:
            start_time (datetime): 本次交易开始时间点
            span (int): 算法执行交易的总时长，以秒为单位
            trade_num (int): 下单的总次数

        Returns:
            list: 本次twap拆单的所有交易时间点
        """
        each_interval = span / trade_num
        trade_time = []
        for i in range(trade_num):
            end_time = start_time + timedelta(seconds=each_interval)
            time_inner = [t for t in self.time_list if end_time > t > start_time ]
            start_time = end_time
            trade_time.append(time_inner[0]) 
        return trade_time

    def buy(self, position):
        price_vol = self.orderbook.get_price_volume(timestamp=self.time_list[0], 
                                    direction='sell', trade_volume=position)
        price_vol_data = pd.DataFrame.from_dict(price_vol) #.sum()
        self.position += position 
        self.position_value += np.sum(price_vol_data.loc['price'] * price_vol_data.loc['volume'])
        avg_price =  self.position_value / position
        
        trade_info = {'position_value':self.position_value, 'position':self.position, 'direction':'buy', 'avg_price':avg_price, 'volume':position, 'trade_detail':price_vol}
        return trade_info

    def sell(self, position):
        # 按 tick sell
        price_vol = self.orderbook.get_price_volume(timestamp=self.time_list[0], 
                                    direction='buy', trade_volume=position)
        price_vol = pd.DataFrame.from_dict(price_vol) #.sum()
        self.position_value -= np.sum(price_vol.loc['price'] * price_vol.loc['volume'])
        avg_price =  self.position_value / position

        trade_info = {'position_value':self.position_value, 'position':self.position, 'direction':'sell', 'avg_price':avg_price, 'volume':position, 'trade_detail':price_vol}
        return trade_info

    def trade(self, direction, total_volume, start_time, span:int, per_volume:int):
        """_summary_

        Args:
            direction (str): 交易方向，'buy' or 'sell'
            total_volume (int): 下单的总手数
            start_time (datetime): 本次交易开始时间点
            span (int): 算法执行交易的总时长，以秒为单位
            per_volume (int): 每次下单的手数

        Returns:
            _type_: _description_
        """
        trade_num = total_volume // per_volume  # 计算下单次数
        trade_time = self.get_trade_ts(start_time, span, trade_num)
        if direction == 'buy':
            for t in trade_time:
                self.trade_info[t] = self.buy(per_volume)
                self.trade_info[t]['position_value'] = self.position_value
                # TODO 存入数据库

        elif direction == 'sell':
            for t in trade_time:
                self.trade_info[t] = self.sell(per_volume)
                # TODO 存入数据库

        return self.trade_info

    
if __name__ == '__main__':
    start_time = datetime(2022,1,4,9,30)
    t = Twap(account='test01')
    trade_info = t.trade(direction='buy', total_volume=10, start_time=start_time, span=120, per_volume=5)
    print(trade_info)
    