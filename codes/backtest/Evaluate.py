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
    # 策略收益率
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
        # 开盘价--今年年末的开盘价 比 去天年末开盘价
        get_lastday['ret'] = np.divide( np.divide(get_lastday[price_name], get_lastday['lastyear_price']) - 1,
                                ((get_lastday['day_num'])/244))
        return get_lastday['ret']

class Evaluate():
    def __init__(self, trade:Trade) -> None:
        self.time_frequency = 240
        self.trade_data = trade.get_all_trade_data(r'C:\Users\shao\Desktop\CUHKSZ\programming\project\trade_data.csv')
        self.commission = trade.commission

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
     
    # 获取每次交易的信息： 买卖价格、卖卖头寸、买卖时的策略净值
    def change_trade_data_to_df(self):
        # 计算主要用 dataframe 形式, 数据存储、读取 后，datetime格式变为了 str，需要修改
        self.trade_data = pd.DataFrame.from_dict(self.trade_data, orient='index')
        self.trade_data['date_time'] = pd.to_datetime(self.trade_data['date_time'])
        self.trade_data.index = pd.to_datetime(self.trade_data.index)
        # 经常需要用到
        self.trade_data['date'] = self.trade_data['date_time'].apply(lambda x:x.date())
        return self.trade_data

    # 获取每次买卖交易的信息，以便求出 '胜率', '盈亏比'等持仓表现数据（适用全仓交易
    def get_each_trade_info(self):
        buy_trade = self.trade_data[self.trade_data['position_chg'] > 0]
        
        buy_trade = buy_trade[['date_time', 'value','cost']]
        buy_trade.reset_index(drop=True, inplace=True)

        # 以 字典嵌套 dataframe 的形式存储数据
        each_trade_info = buy_trade #{'buy':buy_trade, 'sell':sell_trade}
        print('trade_Data:\n', each_trade_info)
        return each_trade_info

    # 获取最大回撤，最大回撤时间
    def get_max_drawdown(self) -> DataFrame:
        '''
        Return
            max_dd_data [dataframe]     含字段['year', 'max_drawdown', 'max_drawdown_time']
        '''
        price_data = self.trade_data
        
        price_data['cummax_price'] = price_data['value'].cummax()
        price_data['dd'] = -np.subtract(price_data.loc[:,'cummax_price'], price_data.loc[:,'value'])
        price_data['dd_ratio'] = np.divide( price_data.loc[:,'dd'], price_data.loc[:,'cummax_price'])
        self.all_drawdown_ratio = price_data['dd_ratio'].to_dict()

        # 年度   最大回撤 & 最大回撤时间
        idx = price_data.resample('y')['dd_ratio'].idxmin()
        max_dd_data = price_data.loc[idx,:][['dd_ratio']]
        max_dd_data['year'] = max_dd_data.index.year
        max_dd_data.reset_index(inplace=True)
        max_dd_data.rename(columns={'index':'max_drawdown_time','dd_ratio':'max_drawdown'}, inplace=True)
        #self.year_drawdown_ratio = max_dd_data.to_dict('index')
        
        # 总的  最大回撤 和 最大回撤时间
        self.max_drawdown = price_data['dd_ratio'].min()
        self.max_drawdown_time = price_data['date_time'].iloc[price_data['dd_ratio'].argmin()]# 求出在groupby里min值的位置（非index
        return max_dd_data

    # 对于 持仓比例变化的 
    def get_daily_gain(self):
        # 今天的 value - 昨天的 value
        daily_gain = self.trade_data['value'] - self.trade_data['value'].shift(1)
        return daily_gain

    # 只有 0-1仓位时获取
    def get_holding_gain(self,save = True) -> DataFrame:
        # 开平仓收益---> 后续来计算盈亏比 & 胜率
        each_trade = self.trade_data[self.trade_data['position_chg'] > 0]
        
        each_trade = each_trade[['date_time', 'value','all_position_value','cash','cost']]
        each_trade.reset_index(drop=True, inplace=True)
        
        # 计算 开平仓结果数据
        # 计算收益，把 扣除的佣金费用加回去
        each_trade['gain'] = (each_trade['value'] + each_trade['all_position_value']*self.commission)\
                             - each_trade['value'].shift(1) # 计算收益
        each_trade['hold_day'] = (each_trade['date_time'] - each_trade['date_time'].shift(1)).dt.days # 将 timedelta转化为int

        self.holding_data = each_trade.copy()
        if save:
            self.holding_data.to_csv(r'C:\Users\shao\Desktop\CUHKSZ\programming\project\holding_data.csv')
        return self.holding_data

    def get_holding_perform(self) -> DataFrame:
        '''
        Return
            holding_perform     [dateframe] 字段['year', ('hold_day',) 'win_ratio','win_loss_ratio']'''

        # 整数仓位： 计算每次开平仓的收益 --> 算胜率、盈亏比
        if self.position_rule == 'int':
            self.get_holding_gain() # 计算开平仓收益
            self.holding_data.set_index('date_time',inplace=True)
            
            year_hold_perform = self.holding_data['hold_day'].resample("y").mean()
            # series 转化为 dataframe
            year_hold_perform = year_hold_perform.to_frame(name='hold_day')
            year_hold_perform['year'] = year_hold_perform.index.year
            year_hold_perform['win_ratio'] = self.holding_data.resample("y").apply(lambda x:\
                                x[x['gain']>0].gain.count()/ x.gain.count())
            year_hold_perform['win_loss_ratio'] = self.holding_data.resample("y").apply(lambda x:\
                                x[x['gain']>0].gain.mean() /x[x['gain']<=0].gain.mean())
        
        # 非整数仓位： 计算每天的收益 --> 算胜率、盈亏比
        elif self.position_rule == 'fract':    
            daily_gain = self.get_daily_gain() # 获得一个series
            
            year_hold_perform = daily_gain.resample("y").apply(lambda x:x[x>0].count() / x.count())
            year_hold_perform = year_hold_perform.to_frame(name='win_ratio')
            #year_hold_perform['win_loss_ratio'] = daily_gain.resample("y").apply(lambda x:\
            #                    x[x>0].mean() / x[x<=0].mean())
        
        print('year_hold_perform\n', year_hold_perform)
        return year_hold_perform

    def get_volatility(self, who:str = 'benchmark') -> series:
        '''
        Parameter
            who     [str]       可选 {'strategy', 'benchmark'}
        Return
            series  [series]    以 date 为索引 的 收益率序列
        '''
        # 波动率：策略年波动率
        price_dict = {'strategy':'value', 'benchmark':'benchmark_price'}
        # 日度数据 计算年度波动率
        ret_data = get_return(self.trade_data, freq='day', price_name=price_dict[who])
        ret_data.index = pd.to_datetime(ret_data.index)

        stra_vol = ret_data.resample("y").agg(np.std) * np.sqrt(244) # 日度收益率算出来的波动率-->年化
        stra_vol.name = who+'_vol'
        return stra_vol

    def get_sharpe(self, ret_vol_data) -> series:
        # 夏普比率： 策略平均收益率/波动率
        sharpe = np.divide(ret_vol_data['strategy_ret'], ret_vol_data['strategy_vol'])
        sharpe.name = 'sharpe'
        return sharpe
    
    def get_ret_vol(self, who='strategy'):
        '''
        Parameter
            who     [str]       可选 {'strategy', 'benchmark'}
        Return
            series  [series]    以 date 为索引 的 收益率序列
        '''
        price_dict = {'strategy':'value', 'benchmark':'benchmark_price'}
        ret = get_return(self.trade_data, freq='year', price_name=price_dict[who])
        ret.name = who + '_ret'
        vol = self.get_volatility(who=who)
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
        self.change_trade_data_to_df()
      
        # 获取持仓表现： 胜率、盈亏比
        holding_perform = self.get_holding_perform()
        
        # 计算 收益率、波动率、夏普比率
        ret_vol_strategy = self.get_ret_vol(who='strategy')
        ret_vol_benchmark = self.get_ret_vol(who='benchmark')
        sharpe = self.get_sharpe(ret_vol_strategy)

        perform_data = pd.concat([holding_perform, ret_vol_strategy, ret_vol_benchmark,sharpe], axis=1) #
        perform_data['year'] = perform_data.index.year

        max_drawdown = self.get_max_drawdown()
        
        self.evaluate_data = pd.merge(max_drawdown,perform_data,on='year',how='left')
        self.evaluate_data.set_index('year', inplace=True)
        self.save_evaluate_data()
        # 字典形式 
        self.evaluate_data = self.evaluate_data.to_dict('index')
        return self.evaluate_data

    
if __name__ == '__main__':
    trade = Trade([],[])
    analyse = Evaluate(trade)
    
    evaluate_data = analyse.evaluate()
    for key, value in evaluate_data.items():
        print(key, ': ',value)
    #print(evaluate_data)
    
