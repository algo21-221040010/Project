import requests
import pandas as pd

start_time = 1546300800000

ret = pd.DataFrame(columns={'open_time': 0, 'open': 1, 'high': 2, 'low': 3, 'close': 4, 'volume': 5,
                            'close_time': 6, 'quote_volume': 7, 'trades': 8, 'taker_base_volue': 9,
                            'taker_quote_volume': 10, 'ignore': 11})
for i in range(526):
    url = 'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=1000&startTime=' + str(start_time)
    resp = requests.get(url)
    data = resp.json()
    df = pd.DataFrame(data)
    df.columns=ret.columns
    ret = ret.append(df)
    # print(len(ret))

    start_time += 1000 * 60 * 1000

ret['open_time'] = pd.to_datetime(ret['open_time']/1000,unit='s')
ret.set_index(['open_time'],inplace=True)
ret = ret[0:525600]
ret=ret[['open','high','low','close','volume']]
ret.to_csv('binance2.csv')
