'''
根据 评估数据 将策略表现可视化

绘制各种图片并保存：最大损益区间图、策略净值标的净值对比图、最大回撤图

Class & Functions
- Pictures      [class]
    需要调用 Evaluate() , 获取 策略评估数据
    Functions:
        - draw_winLoseTopN         最大损益区间图
        - draw_value_ret           策略净值标的净值对比图
        - draw_rolling_drawdown    最大回撤图
'''


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from pyecharts import options as opts
from pyecharts.charts import Kline,Scatter
import seaborn as sns
import os

from Trade import Trade
from Evaluate import Evaluate, get_return


class Pictures():
    def __init__(self, trade_data) -> None:
        self.time_frequency = 240
        
        self.trade_data = trade_data
        print(trade_data)

        # 转化 trade_data 为 dataframe 格式
        if isinstance(self.trade_data, dict):
            self.change_trade_data_to_df()

    def change_trade_data_to_df(self):
        # 计算主要用 dataframe 形式, 数据存储、读取 后，datetime格式变为了 str，需要修改
        self.trade_data = pd.DataFrame.from_dict(self.trade_data, orient='index')
        self.trade_data['date_time'] = pd.to_datetime(self.trade_data['date_time'])
        self.trade_data.index = pd.to_datetime(self.trade_data.index)

        self.trade_data['date'] = self.trade_data['date_time'].apply(lambda x:x.date())

    def draw_trading_signal_with_kline(self):
        # 数据
        data = self.trade_data.copy()
        # 买卖信号数据（ ==>> list格式 ）
        buy_date = list(data[data.signal > 0].index)
        buy = list(data[data.signal > 0].trade_price)
        sell_date = list(data[data.signal < 0].index)
        sell = list(data[data.signal < 0].trade_price)
        
        # K线数据
        kdata = pd.read_csv(r'data\202202data.csv', index_col=2)
        kdata.index = pd.to_datetime(kdata.index)
        xaxis = list(kdata.index.tolist())
        kdata = kdata.loc[:,['OpenPrice','ClosePrice','LowPrice','HighPrice']].to_dict('split')['data'] 

        # 绘图  
        kline = (Kline()
                    .add_xaxis(["{}".format(i) for i in xaxis])
                    .add_yaxis("kline", kdata)
                    .set_global_opts(
                        yaxis_opts = opts.AxisOpts(is_scale=True),#type_="value",
                        xaxis_opts = opts.AxisOpts(is_scale=True),
                        title_opts = opts.TitleOpts(title="Kline & Signal"),
                        # 区域缩放配置 DataZoomOpts
                        datazoom_opts = opts.DataZoomOpts(type_='slider', range_start=0, range_end=1500, orient='horizontal')
                        )
                    )
        buysignal = (Scatter()
                        .add_xaxis( ["{}".format(i) for i in buy_date])
                        .add_yaxis("buy signal", buy, symbol_size = 15, symbol = 'triangle',
                                    label_opts = opts.LabelOpts(is_show=False))#散点旁不显示数据label
                        .set_global_opts(
                            yaxis_opts = opts.AxisOpts(is_scale=True),
                            xaxis_opts = opts.AxisOpts(is_scale=True),
                            datazoom_opts = opts.DataZoomOpts(type_='slider',range_start=0,range_end=1500,orient='horizontal')
                            )
                        )
        sellsignal = (Scatter()
                        .add_xaxis( ["{}".format(i) for i in sell_date])
                        .add_yaxis("sell signal", sell, symbol_size=15, symbol='triangle',symbol_rotate=180,
                                    color='green',label_opts=opts.LabelOpts(is_show=False))#散点旁不显示数据label
                        .set_global_opts(
                            yaxis_opts = opts.AxisOpts(is_scale=True),
                            xaxis_opts = opts.AxisOpts(is_scale=True),
                            datazoom_opts = opts.DataZoomOpts(type_='slider', range_start=0, range_end=100, orient='horizontal')
                            )
                        )
        # K线 和 买卖信号显示在一张图中
        kline.overlap(buysignal).overlap(sellsignal)
        kline.render(r'result/kline_signal.html') 
        return kline
        
    # holding gain
    def draw_winLoseTopN(self, n=3):
        # 获取 Top n 盈亏的 买入、卖出index
        data = self.trade_data.copy()
        pos_perform = pd.read_csv('result\holding_data.csv')
        
        pos_perform.loc[:,'gain_rank_ds'] = pos_perform['gain'].rank(method='first',ascending=False) # 自大到小排列
        pos_perform.loc[:,'gain_rank_as'] = pos_perform['gain'].rank(method='first',ascending=True) # 自小到大排列
        win_topN_buy = list(pos_perform.shift(1)[pos_perform['gain_rank_ds']<=n].date_time)
        win_topN_sell = list(pos_perform[pos_perform['gain_rank_ds']<=n].date_time)
        lose_topN_buy = list(pos_perform.shift(1)[pos_perform['gain_rank_as']<=n].date_time)
        lose_topN_sell = list(pos_perform[pos_perform['gain_rank_as']<=n].date_time)
        win_topN = [win_topN_buy, win_topN_sell]
        lose_topN = [lose_topN_buy, lose_topN_sell]

        # 画图
        # 将策略净值放缩到和 r_open初始值一样的水平上
        data.loc[:,'stra_Val'] = data['value'] #* data['r_open'].iloc[0]/data['value'].iloc[0]
        
        data.set_index(['date_time'], inplace=True)
        highest = data['value'].max()
        lowest = data['value'].min()
        buy_idx = list(data[data.position_chg > 0].index)
        sell_idx = list(data[data.position_chg < 0].index)
        
        plt.figure(figsize=(15, 7))
        
        plt.plot(data['stra_Val'], label="strategy value",color='r',linewidth=1)
        plt.plot(data['stra_Val'][buy_idx],'g^',label="buy", markersize=5)
        plt.plot(data['stra_Val'][sell_idx],'bv',label="sell", markersize=5)

        # 高亮 TOP n的盈亏区间
        if len(win_topN[0])<n:
            n = len(win_topN[0])
            print(f'trading signals are less than {n}!')
            #raise NameError('trading signals are less than N!')
        if len(win_topN[0])>0:
            for i in range(n):
                plt.fill_between(np.array(data.loc[win_topN[0][i]:win_topN[1][i]].index),
                                lowest, highest ,facecolor='red',alpha=0.3)
                plt.fill_between(np.array(data.loc[lose_topN[0][i]:lose_topN[1][i]].index),
                                lowest, highest,facecolor='green', alpha=0.3)
            plt.legend(loc=0)
            plt.show()#savefig(self.savefig_path + "trading_sig.png")
            plt.close()
        data.reset_index(inplace=True)
    
    def draw_value(self):
        data = self.trade_data.copy()

        data['ret'] = data['value'].pct_change()
        data.loc[:, 'cummax_price'] = data['value'].cummax()
        data.loc[:, 'dd'] = -np.subtract(data.loc[:, 'cummax_price'], data.loc[:, 'value'])
        data.loc[:, 'dd_ratio'] = np.divide(data.loc[:, 'dd'], data.loc[:, 'cummax_price'])

        # 画图
        fig = plt.figure(figsize=(10, 8))
        gs = GridSpec(4, 1, figure=fig)
        ax1 = fig.add_subplot(gs[0,0])
        plt.bar(data[data['ret']>=0].index, data[data['ret']>=0]['ret'], color='r', edgecolor='r')
        plt.bar(data[data['ret']<0].index, data[data['ret']<0]['ret'], color='g', edgecolor='g')
        plt.ylabel('daily return')

        ax2 = fig.add_subplot(gs[1:2, 0])
        plt.bar(data.index, height=data['dd_ratio'])
        plt.ylabel("策略回撤率")

        ax3 = fig.add_subplot(gs[2:4, 0])
        plt.plot(data['value'], 'k', label='benchmark value')
        plt.legend()
        plt.ylabel('value')
        plt.grid(visible=True)
        plt.tight_layout()
        plt.show()  # savefig(self.savefig_path + "trading_sig.png")
        plt.close()
    
    def draw_rolling_drawdown(self):
        '''
        Function
            求滚动回撤率序列，并求出总的最大回撤和最大回测时间
            绘图 策略回撤率
        Parameters
            price_data  [dataframe]  数据[['date_time','bench_netVal']]
            allocation  [int]        初始资金（和策略净值 bench_netVal 配套）
        Return
            rolling_d  [dataframe]  年度最大回撤数据[['year','dd_ratio','date_time']]
            drawdown_list [list]    回撤数据 [最大回撤, 最大回撤时间]
        '''
        # 取最大值序列，和当前的price减一下得到新序列，最大回测 = 新序列的最大值/最大值序列
        price_data = self.trade_data.copy()
        price_data.loc[:,'cummax_price'] = price_data['value'].cummax()
        price_data.loc[:,'dd'] = -np.subtract(price_data.loc[:,'cummax_price'], price_data.loc[:,'value'])
        price_data.loc[:,'dd_ratio'] = np.divide( price_data.loc[:,'dd'], price_data.loc[:,'cummax_price'])
        
        plt.bar(price_data.index, height=price_data['dd_ratio'])
        plt.title("策略回撤率")
        plt.show()#savefig(self.savefig_path+"_drawdown_ratio.png")
        plt.close()
    
    def draw(self):
        # self.draw_winLoseTopN()
        # self.draw_value()
        # self.draw_rolling_drawdown()
        self.draw_trading_signal_with_kline()

    
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
    p = Pictures(trade_data)
    # print(type(p).__name__)
    p.draw()
    
