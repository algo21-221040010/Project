"""
创建和读取 orderbook 数据
"""
import pandas as pd
from datetime import datetime


class OrderBook():
    def __init__(self, data, symbol='IF2206') -> None:
        self.orderbook = data
    
    def get_price_volume(self, datetime, direction, trade_volume):
        prefix = direction.title() + 'Price'
        prices = [prefix+'01', prefix+'02', prefix+'03', prefix+'04', prefix+'05']
        prefix = direction.title() + 'Volume'
        volumes = [prefix+'01', prefix+'02', prefix+'03', prefix+'04', prefix+'05']

        trade_detail = {}
        current_vol = 0
        i = 0
        while current_vol < trade_volume and i <= 4:
            volume = self.orderbook.get(datetime).get(volumes[i])
            price = self.orderbook.get(datetime).get(prices[i])
            this_trade_vol = min(volume, trade_volume - current_vol)
            # 交易的 量、价 详情
            trade_detail[i] = {'price':price, 'volume':this_trade_vol}
            current_vol += this_trade_vol
            i += 1
        
        if current_vol < trade_volume:
            raise ValueError(f"Cannot {direction} {trade_volume} unit at {datetime}! Please trade less than {current_vol} unit.")
        return trade_detail

    def get_mid_price(self, datetime):
        bid = self.orderbook.get(datetime).get('BuyPrice01')
        ask = self.orderbook.get(datetime).get('SellPrice01')
        return (bid + ask) / 2


def get_orderbook_data(path=r'data\202202bidask.csv'):
    data = pd.read_csv(path)
    data = data.set_index('TradingTime')
    data.index = pd.to_datetime(data.index)
    time_list = list(data.index)
    data_dict = data.to_dict('index')
    return data_dict, time_list


if __name__ == '__main__':
    data = pd.read_csv(r"C:\Users\shao\Documents\WeChat Files\wxid_kje1iu6rjxry22\FileStorage\File\2022-05\bidask(1).csv")
    # print(data)
    data = data.set_index('TradingTime')
    data.index = pd.to_datetime(data.index)
    time_list = list(data.index)
    data_dict = data.to_dict('index')
    # print(data_dict)

    ob = OrderBook(data_dict, symbol='IF2206')
    ts = time_list[0] # datetime(2022, 1, 4, 9,37,55,9)
    print(ts)
    # print(data_dict.get(ts))
    price = ob.get_price_volume(ts, 'buy', 5)
    print(price)