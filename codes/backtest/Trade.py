'''
根据因子信号进行交易

Class
- Stock  进行单只股票的 买、卖、更新当日市值 等操作
- Trade  根据策略信号 进行 买buy()、卖sell()、更新持仓净值hold() 等操作
    - 需调用 Stock 类

Return
- trade_data [dict]  {date_time: {
                            'date_time','all_position_value', 'cash',
                            'value', 'signal', 'cost',
                            'stock_code','r_price','position', 'position_value'}
                     }
'''
# 买卖都用开盘价
import pandas as pd
import datetime
import os
import pickle


class Stock():
    def __init__(self, stock_code, price_dict):
        # 传入当日 价格数据
        self.stock_code = stock_code

        # 交易数据
        self.r_price = price_dict[stock_code] # get_open_price(stock_code, date, price_dict)

        # 以前的 trade数据
        self.trade_gain = None
        self.position = None
        self.position_value =  None

    def __str__(self) -> str:
        param_list = ['stock_code','r_price','position', 'position_value']
        value = [(name, getattr(self, name)) for name in param_list]
        f_string = ''
        for i, (item, count) in enumerate(value):
            f_string += (f'#{i+1}: '
                         f'{item.title():<15s} = '
                         f'{count}\n')
        return f_string

    def buy(self, position):
        self.position = position
        self.position_value = self.position * self.r_price
        return self.position_value

    def sell(self):
        self.position = 0
        self.position_value = self.position * self.r_price
        #return self.position_value

    def get_current_r_price(self, price_data):
        self.r_price = price_data[self.stock_code]
        return self.r_price

    def get_position_value(self, price_data):
        self.get_current_r_price(price_data)
        self.position_value = self.position * self.r_price
        return self.position_value


class Trade():
    def __init__(self, stock_data, benchmark_data, current_date=datetime.datetime(2011,7,1)):
        self.date_time = current_date #signalData.date_time
        self.time_frequency = 240 # 日度
        self.benchmark_data = benchmark_data
        #self.benchmark_price = benchmark_price[current_date]#get_refactor_open_price('000001.SH', current_date)
        self.stock_data = stock_data
        #self.stock_prices = stock_data[current_date] # get_refactor_open_price('000001.SH', current_date)
        
        self.trade_data_path = r'C:\Users\shao\Desktop\CUHKSZ\programming\project\trade_data.csv'

        # 参数
        self.allocation = 10000000
        self.commission = 0.0003
        
        self.holding_stock = [] # 存储 stock 实例
        self.holding_stock_code = []
        self.cash = self.allocation   # 初始化现金为上期现金值
        self.cost = None
        self.trade_gain = None
        self.all_position_value = None
        self.value = None
    
    def __str__(self) -> str:
        param_list = ['date_time', 'stock_data', 'benchmark_data',
                    'allocation', 'commission',
                    'all_position_value', 'cash', 'value', 'cost',
                    ]
        value = [(name, getattr(self, name)) for name in param_list]
        f_string = ''
        for i, (item, count) in enumerate(value):
            f_string += (f'#{i+1}: '
                         f'{item.title():<15s} = '
                         f'{count}\n')
        return f_string

    def update(self, date, signal):
        self.date_time = date #signalData.date_time
        self.signal = signal
        self.benchmark_price = self.benchmark_data[date]
        self.stock_prices = self.stock_data[date]
        
    # 买入合约，并获取 头寸净值、策略净值
    def buy(self, stock_list):
        # 创建 stock 实例 列表
        for stock_code in stock_list:
            self.holding_stock.append(Stock(stock_code, self.stock_prices))
            self.holding_stock_code.append(stock_code)
        
        # 对每个股票进行买卖
        self.position_ratio = 1/len(self.holding_stock_code)
        temp_position_value = 0
        for stock in self.holding_stock:
            position = (self.position_ratio * self.cash) // ((1 + self.commission) * stock.r_price * 100) * 100
            stock.buy(position)
            temp_position_value += stock.position_value
                
        self.all_position_value = temp_position_value
        self.cost = self.commission * self.all_position_value

        self.cash = self.cash - self.cost - self.all_position_value
        self.value = self.cash + self.all_position_value
        
    def sell(self, stock_list):
        # 非多即空 和 无空仓 的交易一致
        sold_position_value = 0
        hold_position_value = 0
        #assert len(self.holding_stock_code) == len(set(self.holding_stock_code)), \
        #    'repeated value:{}, {}, {}'.format(self.holding_stock_code, sorted(set(self.holding_stock_code), key=self.holding_stock_code.index),0)
        
        i = 0
        while i < len(self.holding_stock):
            stock = self.holding_stock[i]
            if stock.stock_code in stock_list: # 卖出对应的股票
                stock.get_position_value(self.stock_prices)
                sold_position_value += stock.position_value
                stock.sell()
                self.holding_stock.pop(i)
                self.holding_stock_code.pop(i)
                i -= 1 # 删除之后 列表长度小了一个，要倒退一步
            else:                             # 更新持仓净值
                stock.get_position_value(self.stock_prices)
                hold_position_value += stock.position_value
            i += 1

        #assert len(sold) == len(stock_list), f'sold: {sold}, required to sell: {stock_list}. some stock cannot sell!'
        self.all_position_value = hold_position_value
        self.cost = self.commission * sold_position_value
        self.cash = self.cash - self.cost + sold_position_value

        self.value = self.cash + self.all_position_value
    
    def hold(self):
        # update current position value
        temp_position_value = 0
        for stock in self.holding_stock:
            stock.get_position_value(self.stock_prices)
            temp_position_value += stock.position_value
        self.all_position_value = temp_position_value # 头寸计算用 开盘价
        self.cost = 0
        # cash 不变

    def trade(self, stock_list=None):
        self.stock_list = stock_list
        if self.signal == 1: # 买入
            assert len(stock_list) != 0
            self.buy(stock_list)
                
        elif self.signal == -1: # 卖出持仓股，不持股
            assert len(stock_list) != 0
            assert len(self.holding_stock) >= len(stock_list)
            self.sell(stock_list)
            #sell_cost = self.cost

        elif self.signal == 0: # 无交易
            if len(self.holding_stock) != 0: # 如果有持股，则更新价格数据
                self.hold()
            else:                            # 如果无持股，则持仓价值为 0
                self.all_position_value = 0 
                self.cost = 0   

        self.value = self.all_position_value + self.cash
    
    # 获取 并 存储
    def get_trade_data(self):
        '''
        Return
            trade_data [dict]  {date_time: {
                                    'date_time','all_position_value', 'cash',
                                    'value', 'signal', 'cost',
                                    'stock_code','r_price','position', 'position_value'}
        '''
        param_list = ['date_time','all_position_value', 'benchmark_price',\
                      'cash',  'value', 'signal', 'cost']
        value = {name: getattr(self, name) for name in param_list}

        # 每支个股的数据
        stock_param = ['stock_code','r_price','position', 'position_value']
        if len(self.holding_stock) != 0:
            for i in range(len(self.holding_stock)):
                for name in stock_param:
                    value[name+'_'+str(i+1)] = getattr(self.holding_stock[i], name)

        self.trade_data = {self.date_time: value}
        return self.trade_data

    def show_trading_info(self, stock_list):
        if self.signal > 0:
            print(f'{self.date_time}买入{stock_list}，持仓价值{self.all_position_value:.2f}，剩余{self.cash:.2f}现金')
        elif self.signal < 0:
            print(f'{self.date_time}卖出{stock_list}股票，剩余{self.cash:.2f}现金')
        else:
            print(f'{self.date_time} 无操作，当前持仓价值{self.all_position_value:.2f}，总资产{self.value:.2f}')
        print()

    def save_trade_data(self):
        trade_data = pd.DataFrame.from_dict(self.trade_data, orient='index')
        
        if os.path.exists(os.path.split(self.trade_data_path)[0]):
            if os.path.exists(self.trade_data_path):
                trade_data_before = pd.read_csv(self.trade_data_path, index_col=0) 
                trade_data = pd.concat([trade_data_before,trade_data])
                # 存入文件再读出来后，就发生: date_time 格式变为 str
                trade_data['date_time'] = pd.to_datetime(trade_data['date_time'])
                trade_data.sort_values(by='date_time', ascending=True, inplace=True)  
                trade_data.drop_duplicates(subset='date_time',keep='last', inplace=True)
            else: # 若无 旧数据
                pass
        else:
            os.makedirs(os.path.split(self.trade_data_path)[0])

        trade_data.to_csv(self.trade_data_path, index_label='time_index') #, index=False

    def get_all_trade_data(self,path=None):
        '''
        Return
            trade_data [dict]  {date_time: {
                                    'date_time','all_position_value', 'cash',
                                    'value', 'signal', 'cost',
                                    'stock_code','r_price','position', 'position_value'}
        '''
        if path==None:
            path = self.trade_data_path
        all_trade_data = pd.read_csv(path, index_col='time_index')
        print(all_trade_data)
        all_trade_data = all_trade_data.to_dict(orient='index')
        return all_trade_data

    def run(self, save=True):
        self.trade()
        self.get_trade_data()
        if save:
            self.save_trade_data()
        self.show_trading_info()

def load_obj(name): 
    with open(name, 'rb') as f: 
        return pickle.load(f)

if __name__ == '__main__':
    buy_stock = load_obj(r'data\lossstop(4).pkl')
    all_trade_date = [key for key,value in buy_stock.items()]
    # print(buy_stock)
    # a==a

    # get price data and change into dict
    stock_data = pd.read_csv('data\open.csv', header=0, index_col=0)
    stock_data.index = [(datetime.datetime.strptime(x,'%Y-%m-%d')) for x in stock_data.index]
    stock_prices = stock_data.to_dict(orient='index')
    benchmark = pd.read_csv('data\HS300_open.csv', header=0, index_col=0)
    benchmark.index = [(datetime.datetime.strptime(x,'%Y-%m-%d')) for x in benchmark.index]#pd.to_datetime(benchmark.index)
    benchmark_price = benchmark['OPEN'].to_dict() 

    # create instance
    trade = Trade(stock_prices, benchmark_price, current_date=all_trade_date[0]) # 传入数据
    
    for date in all_trade_date:
        signal = buy_stock[date]['signal']
        # update the backtest data
        trade.update(date, signal)
        #print(trade)
        if signal==0:
            trade.trade([])
        else:
            trade.trade(['000155.SZ'])# buy_stock[date]['stocks']
        trade.get_trade_data()
        #print(trade.trade_data)
        trade.show_trading_info(['000155.SZ']) # buy_stock[date]['stocks']
        trade.save_trade_data()
        
    trade.get_all_trade_data()
