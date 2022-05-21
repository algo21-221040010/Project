import pandas as pd
import datetime

from Strategy import Strategy

from Trade import Stock, Trade #, load_obj
from Evaluate import Evaluate
from Pictures import Pictures

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

    
### 获取 signal
closes = pd.read_csv('close.csv')
closes.date = pd.to_datetime(closes.date)
highs = pd.read_csv('high.csv')
lows = pd.read_csv('low.csv')

my_strategy = Strategy(closes, highs, lows)
my_strategy.select_res()
my_strategy.generate_signal()
buy_stock = my_strategy.res       # signal

### 获取 回测价格数据
# buy_stock = load_obj(r'data\lossstop(4).pkl')
all_trade_date = [key for key,value in buy_stock.items()]

# get price data and change into dict
stock_data = pd.read_csv('data\open.csv', header=0, index_col=0)
stock_data.index = [(datetime.datetime.strptime(x,'%Y-%m-%d')) for x in stock_data.index]
stock_prices = stock_data.to_dict(orient='index')
benchmark = pd.read_csv('data\HS300_open.csv', header=0, index_col=0)
benchmark.index = [(datetime.datetime.strptime(x,'%Y-%m-%d')) for x in benchmark.index]#pd.to_datetime(benchmark.index)
benchmark_price = benchmark['OPEN'].to_dict() 

#### 模拟交易
# create instance
trade = Trade(stock_prices, benchmark_price, current_date=all_trade_date[0]) # 传入数据

for date in all_trade_date:
    signal = buy_stock[date]['signal']
    # update the backtest data
    trade.update(date, signal)
    trade.trade(buy_stock[date]['stocks'])
    trade.get_trade_data()
    trade.show_trading_info(buy_stock[date]['stocks'])
    trade.save_trade_data()
    
trade.get_all_trade_data()

#### 策略评估
analyse = Evaluate(trade)
evaluate_data = analyse.evaluate()
#print(evaluate_data)

#### 绘图
picture = Pictures(analyse)
picture.paint()



# 数据导入国内股债收盘价
# from Evaluate import *
# from Pictures import Pictures 
# from TWAP import Twap

# import pickle
# def load_obj(name): 
#     with open(name, 'rb') as f: 
#         return pickle.load(f)
# signal = load_obj(r'data\signal.pkl')
# signal_df = pd.DataFrame.from_dict(signal, 'index')
# signal_df.index = pd.to_datetime(signal_df.index)
# signal = signal_df.to_dict().get(0)
# # print(signal_df)
# # keys = []
# # for key, value in signal:
# #     keys.append(pd.to_datetime(key)
# # signal = dict(zip([],[](]))
# # print(signal)

# trade_data = pd.read_csv(r'data\202202bidask.csv', index_col=1)
# print(trade_data)
# trade_data.index = pd.to_datetime(trade_data.index)

# trade_dt = list(trade_data.index)
# trade_price = trade_data['BuyPrice01'].to_dict()

# trade_dict = {}
# # 调用 Trade 类，进行模拟交易
# trade = Trade()  
# for date in trade_dt:
#     trade.update(date, price=trade_price[date], signal=signal[date])
#     trade_dict[date] = trade.trade()

# trade_data = pd.DataFrame.from_dict(trade_dict, 'index')  # 获得交易持仓净值数据
# trade_data.index = pd.to_datetime(trade_data.index)
# # 回测指标分析
# analyse = Evaluate(trade_data)
# evaluate_data = analyse.evaluate()

# p = Pictures(trade_data)
# print(type(p).__name__)
# # Pictures.draw_value_ret(trade_data)