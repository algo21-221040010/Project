from pymysql import *
from sqlalchemy import create_engine
import pandas as pd
import talib

def SMA(dataframe, column, n=5):
    close = dataframe[column].values
    SMA = talib.SMA(close,n)
    return SMA 

def BBANDS(dataframe, column,timeperiod = 5):
    close = dataframe[column].values
    # MA_Type: 0=SMA, 1=EMA, 2=WMA, 3=DEMA, 4=TEMA, 5=TRIMA, 6=KAMA, 7=MAMA, 8=T3 (Default=SMA)
    upper, middle, lower = talib.BBANDS(close , timeperiod , matype = talib.MA_Type.EMA)
    return upper, middle, lower

def MACD(dataframe, column, fast=12, slow=26, signal=9):
    close = dataframe[column].values
    MACD_macd,MACD_macdsignal,MACD_macdhist = talib.MACD(close, fastperiod=fast, slowperiod=slow, signalperiod=signal)
    return MACD_macd,MACD_macdsignal,MACD_macdhist

def RSI(dataframe, column, timeperiod=14):
    close = dataframe[column].values
    rsi = talib.RSI(close,timeperiod)
    return rsi 

def CCI(dataframe, columnClose, columnHigh, columnLow, timeperiod=14):
    close = dataframe[columnClose].values
    high = dataframe[columnHigh].values
    low = dataframe[columnLow].values
    cci = talib.CCI(high, low, close, timeperiod)
    return cci

def WILLR(dataframe, columnClose, columnHigh, columnLow, timeperiod=14):
    close = dataframe[columnClose].values
    high = dataframe[columnHigh].values
    low = dataframe[columnLow].values
    willr = talib.WILLR(high, low, close, timeperiod)
    return willr

def KDJ(dataframe, columnClose, columnHigh, columnLow, fastk=5, slowk=3, slowd=3):
    close = dataframe[columnClose].values
    high = dataframe[columnHigh].values
    low = dataframe[columnLow].values
    k,d = talib.STOCH(high, low, close, fastk_period=fastk, slowk_period=slowk, slowk_matype=0, slowd_period=slowd, slowd_matype=0)
    j = []
    for i1,i2 in zip(k,d):
        j.append(3*i1-2*i2)
    return k,d,j

def volumeRatio(dataframe, columnVolume):
    volume = dataframe[columnVolume].tolist()
    n = len(volume)
    vr = []
    sum = 0
    for i in list(range(n)):
        sum += volume[i]
        vr.append(sum/(i+1))
    return vr

def priceChange(dataframe, columnClose):
    price = dataframe[columnClose].tolist()
    n = len(price)
    absChg = []
    retChg = []
    for i in list(range(n)):
        if i - 0 < 0.0000001:
            absChg.append(0)
            retChg.append(0)
        else:
            absChg.append(abs(price[i]-price[i-1]))
            retChg.append((price[i]-price[i-1])/price[i-1])
    return absChg, retChg

def priceChangeAfterThrityDays(dataframe, columnClose):
    price = dataframe[columnClose].tolist()
    n = len(price)
    retChgAfter = []
    for i in list(range(n)):
        if i+31-n < 0.0000001:
            retChgAfter.append((price[i+30]-price[i])/price[i])
        else:
            retChgAfter.append(0)
    return retChgAfter

def Tolabel(listToLable):
    
    listToLable1 = []
    for i in listToLable:
        listToLable1.append(i)
    print(listToLable)
    listToLable1.sort()
    print(listToLable)
    # print(listToLable)
    n=len(listToLable)
    k0 = int(n*0.3)
    l0 = int(n*0.7)
    k = listToLable1[k0]
    l = listToLable1[l0]
    print(n,k,l)
    label = []
    for i in list(range(n)):
        a = listToLable[i]
        if a > l:
            label.append(1)
        elif a < k:
            label.append(-1)
        else:
            label.append(0)
    print(label)
    return label

def getDataForBackTestAnalysis():

    host='rm-wz92xxsa5315l05g2so.mysql.rds.aliyuncs.com'
    port=3306
    user='algo76'
    passwd="123456@CUHKSZ"
    db='mfe5210project'

    conn = connect(host=host,port=port
                ,user=user,passwd=passwd
                ,db=db,charset='utf8')
    cursor = conn.cursor()

    data =  pd.read_sql("SELECT * FROM `Market_data_Backtest`",con = conn)

    SMA5 = SMA(data,"ClosePrice",n=5)
    SMA10 = SMA(data,"ClosePrice",n=10)
    SMA20 = SMA(data,"ClosePrice",n=20)
    SMA30 = SMA(data,"ClosePrice",n=30)
    SMA60 = SMA(data,"ClosePrice",n=60)

    upper, middle, lower = BBANDS(data,"ClosePrice",timeperiod = 5)

    MACD_macd,MACD_macdsignal,MACD_macdhist = MACD(data,"ClosePrice", fast=12, slow=26, signal=9)

    rsi = RSI(data,"ClosePrice", timeperiod=14)

    cci = CCI(data,"ClosePrice",  "HighPrice", "LowPrice", timeperiod=14)

    willr = WILLR(data,"ClosePrice",  "HighPrice", "LowPrice", timeperiod=14)

    k,d,j = KDJ(data,"ClosePrice",  "HighPrice", "LowPrice", fastk=5, slowk=3, slowd=3)

    v = volumeRatio(data,"Volume")

    absChg, retChg = priceChange(data, "ClosePrice")

    retChgAfter = priceChangeAfterThrityDays(data, "ClosePrice")

    label = Tolabel(retChgAfter)

    data['sma5'] = SMA5
    data['sma10'] = SMA10
    data['sma20'] = SMA20
    data['sma30'] = SMA30
    data['sma60'] = SMA60

    data['BOLLupper'] = upper
    data['BOLLmiddle'] = middle
    data['BOLLlower'] = lower

    data['MACD_macd'] = MACD_macd
    data['MACD_macdsignal'] = MACD_macdsignal
    data['MACD_macdhist'] = MACD_macdhist

    data['rsi'] = rsi

    data['cci'] = cci
    data['WR'] = willr
    data['KDJk'] = k
    data['KDJd'] = d
    data['KDJj'] = j

    data["volumeRatio"] = v
    data["absPriceChange"] = absChg
    data["retPriceChange"] = retChg
    data["retChgAfter"] = retChgAfter
    data["label"] = label


    # data.to_csv('202202data.csv')
    return data
