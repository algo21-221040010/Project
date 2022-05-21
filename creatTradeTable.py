# database
# mysql -h rm-wz92xxsa5315l05g2so.mysql.rds.aliyuncs.com -u algo76 -p
import os
from pymysql import *
from sqlalchemy import create_engine
import pandas as pd


# MySQL操作函数
class MySQLOperation:
    def __init__(self, host, port, db, user, passwd, charset='utf8'):
        # 参数初始化
        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.passwd = passwd
        self.charset = charset
        self.conn = None
        self.cursor = None

    def open(self):
        # 打开数据库连接
        self.conn = connect(host=self.host,port=self.port
                            ,user=self.user,passwd=self.passwd
                            ,db=self.db,charset=self.charset)
        # 使用 cursor() 方法创建一个游标对象 cursor
        self.cursor = self.conn.cursor()

    def close(self):
        # 断开数据库连接
        self.cursor.close()
        self.conn.close()

    def Execute_Code(self, sql):
        # 执行SQL代码：建表、删表、插入数据
        try:
            self.open()               # 打开数据库连接
            self.cursor.execute(sql)  # 使用execute()方法执行SQL
            self.conn.commit()        # 提交到数据库执行
            self.close()              # 断开数据库连接
        except Exception as e:
            self.conn.rollback()      # 发生错误时回滚
            self.close()              # 断开数据库连接
            print(e)

    def Select_Code(self, sql):
        # 执行SQL代码，查询数据
        try:
            self.open()                        # 打开数据库连接
            self.cursor.execute(sql)           # 使用execute()方法执行SQL
            result = self.cursor.fetchall()    # 获取所有记录列表
            self.close()                       # 断开数据库连接
            return result                      # 返回查询数据
        except Exception as e:
            self.conn.rollback()               # 发生错误时回滚
            self.close()                       # 断开数据库连接
            print(e)


host='rm-wz92xxsa5315l05g2so.mysql.rds.aliyuncs.com'
port=3306
user='algo76'
passwd="123456@CUHKSZ"
db='mfe5210project'
# 方法实例化
MySQL = MySQLOperation(host, port, db, user, passwd)

# 建表
sql_str = '''CREATE TABLE Market_data_Trade (
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
MySQL.Execute_Code(sql_str)
