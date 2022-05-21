import pandas as pd
import datetime

from database.downloadBackTestData import *
from strategy.resnet import *
from trader.Trade import Trade 
from trader.Evaluate import Evaluate
from trader.Pictures import Pictures

# 获取 signal
lr, num_epochs, batch_size = 0.05, 5, 250
dfTemp = getDataForBackTestAnalysis()
df = dfTemp.iloc[:4500,1:]
df_test = dfTemp.iloc[4500:9000,1:]

train_iter = load_array(preprocess(df), batch_size=batch_size)
train(net(), train_iter, num_epochs, lr)

x_test, y_test = preprocess(df_test)
y_test_hat = net()(x_test.float()).argmax(axis=1)

signal=np.array(y_test_hat)
signal=np.where(signal<0, 0, signal)
for i,_ in enumerate(signal):
    n=len(signal)
    if signal[i]==1 and i+30<n:
        signal[i+30]=-1
    if i==n-1:
        signal[i]=-1

signal=dict(zip(x_test['TradingTime'], signal))

# 导入回测数据
trade_data = getDataForBackTestAnalysis()
trade_dt = list(trade_data.index)
trade_price = trade_data['OpenPrice'].to_dict()

trade_dict = {}
# 模拟交易
trade = Trade()  
for date in trade_dt:
    trade.update(date, price=trade_price[date], signal=signal[date])
    trade_dict[date] = trade.trade()

trade_data = pd.DataFrame.from_dict(trade_dict, 'index')  # 获得交易持仓净值数据
trade_data.index = pd.to_datetime(trade_data.index)

# 回测指标分析
analyse = Evaluate(trade_data)
evaluate_data = analyse.evaluate()
print(evaluate_data)

# 绘图
picture = Pictures(trade_data)
picture.draw()
