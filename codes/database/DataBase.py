from pymysql import *
from sqlalchemy import create_engine
import pandas as pd

class DataBase():
    def __init__(self,host='rm-wz92xxsa5315l05g2so.mysql.rds.aliyuncs.com',port=3306,user='algo76',passwd="123456@CUHKSZ",db='mfe5210project'):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.db = db
        self.conn = None
        self.cursor = None

    def logInDataBase(self):
        self.conn = connect(host=self.host,port=self.port,user=self.user,passwd=self.passwd,db=self.db,charset='utf8')
        self.cursor = self.conn.cursor()

    
    def logOutDataBase(self):
        self.cursor.close()
        self.conn.close()
    
    def excuteSql(self, sqlStr):
        self.cursor.execute(sqlStr)
        self.conn.commit()
        result = self.cursor.fetchall()
        return result


if __name__=='__main__':
    DB = DaseBase()
    DB.logInDataBase()

    # create table
    sqlStrForCreatingMarketTable = '''CREATE TABLE Market_data_Trade (
        TradingDate int,
        TradingTime datetime,
        Symbol varchar(6),
        OpenPrice decimal(9,3),
        LastPrice decimal(9,3),
        HighPrice decimal(9,3),
        LowPrice decimal(9,3),
        SettlePrice decimal(9,3),
        PreSettlePrice decimal(9,3),
        ClosePrice decimal(9,3),
        PreClosePrice decimal(9,3),
        TradeVolume decimal(19,0),
        TotalVolume decimal(19,2),
        TradeAmount decimal(19,3),
        TotalAmount decimal(19,3),
        PreTotalPosition decimal(19,2),
        TotalPosition decimal(19,2),
        PrePositionChange decimal(19,2),
        PriceUpLimit decimal(9,3),
        PriceDownLimit decimal(9,3),
        BuyOrSell varchar(1),
        OpenClose Nvarchar(9),
        BuyPrice01 decimal(9,3),
        BuyPrice02 decimal(9,3),
        BuyPrice03 decimal(9,3),
        BuyPrice04 decimal(9,3),
        BuyPrice05 decimal(9,3),
        SellPrice01 decimal(9,3),
        SellPrice02 decimal(9,3),
        SellPrice03 decimal(9,3),
        SellPrice04 decimal(9,3),
        SellPrice05 decimal(9,3),
        BuyVolume01 decimal(19,2),
        BuyVolume02 decimal(19,2),
        BuyVolume03 decimal(19,2),
        BuyVolume04 decimal(19,2),
        BuyVolume05 decimal(19,2),
        SellVolume01 decimal(19,2),
        SellVolume02 decimal(19,2),
        SellVolume03 decimal(19,2),
        SellVolume04 decimal(19,2),
        SellVolume05 decimal(19,2),
        Delta decimal(9,4),
        PreDelta decimal(9,4),
        SettleGroupID varchar(9),
        SettleID decimal(9,0),
        Change_ decimal(9,3),
        ChangeRatio decimal(9,4),
        ContinueSign varchar(6),
        Market varchar(5),
        UNIX decimal(19,0),
        PositionChange decimal(19,2),
        ContinueSignName nvarchar(6),
        SecurityID decimal(19,0),
        ShortName nvarchar(20),
        AveragePrice decimal(9,3),
        OrderRate decimal(9,4),
        OrderDiff decimal(19,2),
        Amplitude decimal(9,4),
        VolRate decimal(9,4),
        SellVOL decimal(19,2),
        BuyVOL decimal(19,2))'''

    resultForCreatingMarketTable = DB.excuteSql(sqlStrForCreatingMarketTable)

    sqlStrForCreatingBackTestTable = '''CREATE TABLE Market_data_Backtest (
                            TradingDate int,
                            TradingTime datetime,
                            Symbol varchar(6),
                            OpenPrice decimal(9,3),
                            ClosePrice decimal(9,3),
                            HighPrice decimal(9,3),
                            LowPrice decimal(9,3),
                            Change decimal(9,3),
                            ChangeRatio decimal(9,3),
                            Position int,
                            Volume decimal(19,3),
                            Amount decimal(19,3))'''

    resultForCreatingBackTestTable = DB.excuteSql(sqlStrForCreatingBackTestTable)

    sqlStrForCreatingBackTestTable = '''CREATE TABLE Market_data_Backtest (
                            TradingDate int,
                            TradingTime datetime,
                            Symbol varchar(6),
                            OpenPrice decimal(9,3),
                            ClosePrice decimal(9,3),
                            HighPrice decimal(9,3),
                            LowPrice decimal(9,3),
                            Change decimal(9,3),
                            ChangeRatio decimal(9,3),
                            Position int,
                            Volume decimal(19,3),
                            Amount decimal(19,3))'''

    resultForCreatingBackTestTable = DB.excuteSql(sqlStrForCreatingBackTestTable)

