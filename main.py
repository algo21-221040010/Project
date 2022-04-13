import pandas as pd
import datetime

from Strategy import Strategy

from Trade import Stock, Trade #, load_obj
from Evaluate import Evaluate
from Pictures import Pictures


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
