

# 1. What is included in our delivery?
- i. 'code' folder contains all of our code implementations and data we needed. There get five '.py' files,which are *'main.py', 'Strategy.py', 'Trade.py', 'Evaluate.py', 'Pictures.py'* respectively. And 'data' folder contains five csv files, which contain **OHLC of all markets** in the past 10 years and **CSI300’s open price** respectively.
- ii. '回测结果' fold contains all of our **backtest** results.
- iii. '第二组pre.pptx' is the slides for our **presentation**.
- iv. '均线簇量化策略报告.pdf' is our **Trading strategy research report**.
- v. 'Electric Vehicle Industry Research Report.pdf' is our **Research papers on Electric Vehicle Industry**.
- vi. 'Team Member Work.xlsx' shows what our team members have done in our project.

-------------------------------------------------------------------

# 2. How to Run our trategy?
You can simply run the 'main.py', then you can get the backtest results.
Hope u have fun :)

-------------------------------------------------------------------

# 3. Briefly introduction of codes?
There are 5 classes in our folder, and all of these are eventually imported to main.py:
## i. Strategy class: 
### Main Member function: 
  - **select_stock**: the MA stock-select algorithm 
  - **select_res**: run monthly to get the stock pool
  - **generate_signal**: run the RSRS and limit condition daily to get Buy/Sell signals.
  
### Main Member variable:
  - **trade_cal**: Every trade calenders in the past 10 years.
  - **res**: The results of Buy/Sell signal send to backtest.
  - **hold_stocks**: The stocks hold in the backtest and updated everyday.

## ii. Stock class:
### Main Member function:
  - **buy**: calculate the position value of the stock which we need to buy.
  - **sell**: sell the stock, and let the position and position value of the stock be zero.
  - **get_position_value**: update the position value of holding stock.

### Main Member variable:
  - **stock_code**: stock code
  - **r_price**: refactor price of the stock
  - **position**: amount of stock we are holding
  - **position_value**: value of stock we are holding

## iii. Trade class:
### Main Member function: 
  - **update**: update the value of our strategy.
  - **buy**: calculate the position value of the stock which we need to buy.
  - **sell**: sell the stock, and let the position and position value of the stock be zero.
  - **hold**: update the value of our holding stocks and our strategy.
  - **trade**: receive the signal and stock list of one day and trade.
  - **save_trade_data**: save trading data, such as:
    - position value of each stock
    - total position value
    - cash
    - trading cost
    - total value of our strategy

### Main Member variable:
  - **date_time**: current date
  - **allocation**: initial funds in our backtesting
  - **commission**: commission expense, trading cost
        
## iv. Evaluate class:
### Main Member function: 
  - **get_max_drawdown**: calculate the max drawdown of each year
  - **get_holding_perform**: get the gain and loss of each trade and calculate win_ratio, win_loss_ratio(胜率，盈亏比)
  - **get_ret_vol**: calculate the return and volatility of benchmark and our strategy each year
  - **get_sharpe**: calculate the Sharpe of our strategy 
  - **save_evaluate_data**: get metrics that are very important for strategy evaluation and save into 'trade_data.csv':
    - sharpe
    - max drawdown, max drawdown time
    - win ratio, win_loss_ratio
    - return and volatility of our strategy
    - return and volatility of benchmark(CSI 300)

### Main Member variable:
  - **trade_data**: trade data over the whole backtesting period.

## v. Pictures class:
### Member function: 
  - **draw_winLoseTopN**: draw a picture which highlight the top N period of trade which we gain/loss most.
  - **draw_value_ret**: draw the value of our strategy and benchmark, and their ratio which denotes whether our strategy performs better than the benchmark(CSI300) 
  - **draw_rolling_drawdown**: draw the rolling max drawdown
### Main Member variable:
  - **trade_data**: trade data over the whole backtesting period.

