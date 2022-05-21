import datetime
from pymysql import *
from sqlalchemy import create_engine
import pandas as pd

class MarketData():
    def __init__(self,beginTime,conSql,DB,index):
        self.b = beginTime
        self.t = datetime.timedelta(hours = 0, minutes = 1, seconds = 0)
        self.list = index
        self.n = len(self.list)
        self.timeNow = self.b
        self.timeClose = self.b+datetime.timedelta(hours = 5, minutes = 30, seconds = 0)
        self.sql = conSql
        self.cursor = self.sql.cursor()
        self.DB = DB

    def getMarketData(self):
        dictToReturn = {}
        if self.timeNow < self.timeClose:
            sqlGetPrice = "select * from %s where TradingTime = '%s' limit 1"%(self.DB,self.timeNow)
            self.cursor.execute(sqlGetPrice)
            self.sql.commit()
            result = self.cursor.fetchall()
            if result:
                for i in list(range(self.n)):
                    dictToReturn[self.list[i]] = result[0][i]
            # print(dictToReturn)
            self.timeNow += self.t
            return dictToReturn
        print("Market Close")



# mysql element
host='rm-wz92xxsa5315l05g2so.mysql.rds.aliyuncs.com'
port=3306
user='algo76'
passwd="123456@CUHKSZ"
db='mfe5210project'
conn = connect(host=host,port=port
                ,user=user,passwd=passwd
                ,db=db,charset='utf8')
cursor = conn.cursor()



# test
beginTime = datetime.datetime(2022, 2, 7, 9, 30, 00)

current = ["TradingDate" , "TradingTime" , "Symbol" , "OpenPrice" , "LastPrice" , "HighPrice" , "LowPrice" , "SettlePrice" , "PreSettlePrice" , "ClosePrice" , "PreClosePrice" , "TradeVolume" , "TotalVolume" , "TradeAmount" , "TotalAmount" , "PreTotalPosition" , "TotalPosition" , "PrePositionChange" , "PriceUpLimit" , "PriceDownLimit" , "BuyOrSell" , "OpenClose" , "BuyPrice01" , "BuyPrice02" , "BuyPrice03" , "BuyPrice04" , "BuyPrice05" , "SellPrice01" , "SellPrice02" , "SellPrice03" , "SellPrice04" , "SellPrice05" , "BuyVolume01" , "BuyVolume02" , "BuyVolume03" , "BuyVolume04" , "BuyVolume05" , "SellVolume01" , "SellVolume02" , "SellVolume03" , "SellVolume04" , "SellVolume05" , "Delta" , "PreDelta" , "SettleGroupID" , "SettleID" , "Change" , "ChangeRatio" , "ContinueSign" , "Market" , "UNIX" , "PositionChange" , "ContinueSignName" , "SecurityID" , "ShortName" , "AveragePrice" , "OrderRate" , "OrderDiff" , "Amplitude" , "VolRate" , "SellVOL" , "BuyVOL"]
history =["TradingDate","TradingTime","Symbol","OpenPrice","ClosePrice","HighPrice","LowPrice","Change","ChangeRatio","Position","Volume","Amount"]


BackMD = MarketData(beginTime,conn,"Market_data_Backtest",history)
TradeMD = MarketData(beginTime,conn,"Market_data_Trade",current)
for i in list(range(100)):
    # MarketData1 = BackMD.getMarketData()
    MarketData2 = TradeMD.getMarketData()

    # print(MarketData1)
    print(MarketData2)













