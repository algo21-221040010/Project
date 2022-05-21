'''
根据交易结果数据 进行策略评估

计算 最大回撤率、最大回撤时间、胜率、盈亏比、平均持仓周期、策略年收益、策略波动率、
标的年收益、标的年波动率、夏普比率 等指标来对策略进行评估

Class & Functions
- get_return    [function]  获取收益率
- Evaluate      [class]
    需要调用 get_all_trade_data()函数 , 获取当前时刻之前的所有交易数据
    
Return
- perform_data  [dict]  {year: 
                           {'max_drawdown_time', 'max_drawdown',
                            'win_ratio', 'win_loss_ratio',
                            'benchmark_ret', 'benchmark_vol',
                            'strategy_ret', 'strategy_vol', 'sharpe'
                            }
                        }
'''

import numpy as np
import pandas as pd
import os
import datetime
from pandas.core import series
from pandas.core.frame import DataFrame

from Trade import Trade



def get_return(trade_data, freq='day', price_name='benchmark_price') -> series: 
    '''
    Parameter
        trade_data  [dataframe] 含字段['date','benchmark_price']
    Return
        series      [series]    以 date 为索引 的 收益率序列
    '''
    trade_data['date_time'] = trade_data.index
    trade_data['date'] = trade_data.apply(lambda x:datetime.datetime(x.date_time.year, x.date_time.month,
                                             x.date_time.day) , axis=1)
    if freq=='day':
        get_dayLast = trade_data.groupby('date')[price_name].nth(-1)
        get_dayLast.name = 'dayLast'
        d_ret = get_dayLast.reset_index()
        # 日度收益率 : log[Pt/P(t-1)]
        d_ret['ret'] = np.log( np.divide(d_ret['dayLast'].shift(-1), d_ret['dayLast']) )
        d_ret.set_index('date', inplace=True)
        return d_ret['ret']
    
    if freq=='year':
        # 日内频率数据：只保留最后一个数据
        data = trade_data.drop_duplicates(['date'], keep='last')
        # 求一年的天数（主要为求回测区间 第一年 & 最后一年天数，因为不一定恰好选年初开始，年末结束）
        data['day_num'] = data.resample("y")['date'].transform('count')
        # 求 去年年底的价格（第一年则取第一天的值
        first_price = data[price_name].iloc[0]
        get_lastday = data.resample("y")[price_name,'day_num'].nth(-1)            
        get_lastday['lastyear_price'] = get_lastday[price_name].shift(1).fillna(first_price)
        
        # 求年化收益率:  [Pt/P(t-1) - 1] / (Tt-T(t-1)/244)
        get_lastday['ret'] = np.divide( np.divide(get_lastday[price_name], get_lastday['lastyear_price']) - 1,
                                ((get_lastday['day_num'])/244))
        # get_lastday.index = trade_data.index
        return get_lastday['ret']

class Evaluate():
    def __init__(self, trade_data, commission=0.0002) -> None:
        self.time_frequency = 240
        self.trade_data = trade_data
        self.commission = commission

        self.each_trade_info = None # 每次交易的买卖价格、卖卖头寸、买卖时的策略净值
        # 对于0-1仓位还是非整数仓位 的区分
        self.position_rule = 'int' # 'int' or 'fract'

    def __str__(self) -> str:
        param_list = ['date_time','time_frequency', 'trade_data']
        value = [(name, getattr(self, name)) for name in param_list]
        f_string = ''
        for i, (item, count) in enumerate(value):
            f_string += (f'#{i+1}: '
                         f'{item.title():<15s} = '
                         f'{count}\n')
        return f_string


    # 获取每次买卖交易的信息，以便求出 '胜率', '盈亏比'等持仓表现数据（适用全仓交易
    def get_each_trade_info(self):
        buy_trade = self.trade_data[self.trade_data['position_chg'] > 0]
        
        buy_trade = buy_trade[['date_time', 'value','cost']]
        buy_trade.reset_index(drop=True, inplace=True)

        # 以 字典嵌套 dataframe 的形式存储数据
        each_trade_info = buy_trade #{'buy':buy_trade, 'sell':sell_trade}
        return each_trade_info

    def cal_max_drawdown(self, data):
        # data 最好以时间为 index
        cummax_price = data['value'].cummax()
        drawdown = (data['value'] - cummax_price) / cummax_price  # 每天的 回撤率
        max_dd_loc = drawdown.argmin()  # 最大回撤时间点
        max_dd_start = (cummax_price[:max_dd_loc]).idxmax() # 计算这次最大回测对应的开始时间点
        max_dd_start = datetime.datetime.strftime(max_dd_start, '%Y/%m/%d')
        max_dd_end = datetime.datetime.strftime(drawdown.idxmin(), '%Y/%m/%d') 
        return drawdown.min(), f'from {max_dd_start} to {max_dd_end}'

    # 获取最大回撤，最大回撤时间
    def get_max_drawdown_data(self) -> DataFrame:
        price_data = self.trade_data.copy()

        price_data['cummax_price'] = price_data['value'].cummax()
        price_data['dd_ratio'] = (price_data['value'] - price_data['cummax_price']) / price_data['cummax_price']
        self.all_drawdown_ratio = price_data['dd_ratio'].to_dict()

        # 年度   最大回撤 & 最大回撤时间    
        max_dd_data = price_data.resample('W').apply(self.cal_max_drawdown).apply(pd.Series)  # 最后一个apply，将 tuple series转变为两列的dataframe
        max_dd_data.columns=['Maximum Drawdown', 'Maximum Drawdown Period']
        max_dd_data['year'] = max_dd_data.index.year
    
        # 总的  最大回撤 和 最大回撤时间
        self.max_drawdown = price_data['dd_ratio'].min()
        self.max_drawdown_time = price_data['dd_ratio'].argmin()  # 求出在groupby 里 min值的位置（非index
        return max_dd_data

    # 对于 持仓比例变化的 
    def get_daily_gain(self):
        # 今天的 value - 昨天的 value
        daily_gain = self.trade_data['value'] - self.trade_data['value'].shift(1)
        return daily_gain

    # 只有 0-1仓位时获取
    def get_holding_gain(self,save=True) -> DataFrame:
        # 开平仓收益---> 后续来计算盈亏比 & 胜率
        each_trade = self.trade_data[self.trade_data['signal'] > 0]
        
        each_trade = each_trade[['value','position_value','cash']]
        each_trade = each_trade.reset_index()
        
        # 计算 开平仓结果数据
        # 计算收益，把 扣除的佣金费用加回去
        each_trade['gain'] = (each_trade['value'] + each_trade['position_value']*self.commission)\
                             - each_trade['value'].shift(1) # 计算收益
        each_trade['hold_day'] = (each_trade['index'] - each_trade['index'].shift(1)).dt.days # 将 timedelta转化为int

        self.holding_data = each_trade.copy().set_index('index')
        if save:
            self.holding_data.to_csv(r'result\holding_data.csv')
        return self.holding_data

    def get_holding_perform(self) -> DataFrame:
        # 计算每次开平仓的收益 --> 算胜率、盈亏比
        self.get_holding_gain()  # 计算开平仓收益

        win_ratio = self.holding_data.resample("W").apply(lambda x: x[x['gain'] > 0].gain.count() / x.gain.count())
        win_loss_ratio = self.holding_data.resample("W").apply(
            lambda x: x[x['gain'] > 0].gain.mean() / x[x['gain'] <= 0].gain.mean())

        year_hold_perform = pd.concat([win_ratio, win_loss_ratio], axis=1, keys=['win_ratio', 'win_loss_ratio'])
        year_hold_perform['WEEK'] = year_hold_perform.index
        return year_hold_perform

    def get_volatility(self) -> series:
        # 日度数据 计算年度波动率
        ret_data = self.trade_data['value'].pct_change() # get_return(self.trade_data, freq='day', price_name='value')
        stra_vol = ret_data.resample("W").agg(np.std) * np.sqrt(255 * 244)  # 日度收益率算出来的波动率-->年化
        stra_vol.name = 'Annualized Volatility'
        return stra_vol

    def get_sharpe(self, ret_vol_data) -> series:
        # 夏普比率： 策略平均收益率/波动率
        sharpe = np.divide(ret_vol_data['Annualized Return'], ret_vol_data['Annualized Volatility'])
        sharpe.name = 'Sharpe Ratio'
        return sharpe

    def get_calmar(self, data):
        return data['Annualized Return'] / (- data['Maximum Drawdown'])

    def get_ret_vol(self):
        ret = self.trade_data['value'].resample('W').apply(lambda x: ((x[-1]/ x[0]) - 1)/ (len(x)/244))
        ret.name = 'Annualized Return'
        vol = self.get_volatility()
        ret_vol_data = pd.concat([ret, vol], axis=1)
        return ret_vol_data

    def get_result_path(self):
        self.result_path = r'C:\Users\shao\Desktop\CUHKSZ\programming\project\evaluate_data.csv'

    def save_evaluate_data(self):
        self.get_result_path()
        if not os.path.exists(os.path.split(self.result_path)[0]):
            os.makedirs(os.path.split(self.result_path)[0])     
        self.evaluate_data.to_csv(self.result_path, index_label='year') #, index=False)

    def evaluate(self):      
        # 获取持仓表现： 胜率、盈亏比
        holding_perform = self.get_holding_perform()
        
        # 计算 收益率、波动率、夏普比率
        ret_vol_strategy = self.get_ret_vol()
        sharpe = self.get_sharpe(ret_vol_strategy)

        perform_data = pd.concat([holding_perform, ret_vol_strategy, sharpe], axis=1) #
        # perform_data['year'] = perform_data.index.year

        max_drawdown = self.get_max_drawdown_data()
        print(max_drawdown)
        print(perform_data)
        
        self.evaluate_data = pd.merge(max_drawdown,perform_data,left_index=True, right_index=True, how='left')
        self.evaluate_data['Calmar Ratio'] = self.get_calmar(self.evaluate_data)

        self.evaluate_data.set_index('year', inplace=True)
        self.save_evaluate_data()
        # 字典形式 
        # self.evaluate_data = self.evaluate_data.to_dict('index')
        return self.evaluate_data

    
if __name__ == '__main__':
    # trade = Trade()
    # 数据导入国内股债收盘价
    from Trade import Trade
    from Pictures import Pictures 
    # from TWAP import Twap

    import pickle
    def load_obj(name): 
        with open(name, 'rb') as f: 
            return pickle.load(f)
    signal = load_obj(r'data\signal.pkl')
    
    trade_data = pd.read_csv(r'data\202202data.csv', index_col=2)
    trade_data.index = pd.to_datetime(trade_data.index)
    
    trade_dt = list(trade_data.index)
    trade_price = trade_data['OpenPrice'].to_dict()

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

    print(evaluate_data)
    # p = Pictures(trade_data)
    # # print(type(p).__name__)
    # p.draw()
    
