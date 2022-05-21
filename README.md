# 1. Our group member
- Shao Kai邵凯, Diao Xingning刁兴宁, Zhuo Jinjun卓金俊, Jiang Yilu江一橹
# 2. What is included in our delivery?
- i. 'code' folder contains all of our **codes implementations** and data we needed. There get three folders in it, namely:
  - '**database**' folder, which contains codes which read data from database and write data in it. 
  - '**strategy**' folder contains our strategy which generates signals.
  - '**trader**' folder contains the main components of our backtesting and algo trading system.

- ii. 'data' folder contains data we need to generate signals and backtest our strategy.
- iii. 'result' folder contains all of our **backtest** results as well as pictures.
- iv. '5210project - Group1(the 4th presentation).pptx' is the slides for our **presentation**.

-------------------------------------------------------------------

# 3. How to Run our trategy?
You can simply run the 'codes/main.py', then you can get the backtest results.
Hope u have fun :)

-------------------------------------------------------------------

# 4. Briefly introduction of Main Classes
## i. Trade class:
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
        
## ii. Evaluate class:
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

## iii. Pictures class:
### Member function: 
  - **draw_winLoseTopN**: draw a picture which highlight the top N period of trade which we gain/loss most.
  - **draw_value_ret**: draw the value of our strategy and benchmark, and their ratio which denotes whether our strategy performs better than the benchmark(CSI300) 
  - **draw_rolling_drawdown**: draw the rolling max drawdown
### Main Member variable:
  - **trade_data**: trade data over the whole backtesting period.

