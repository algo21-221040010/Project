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
sql_str = '''CREATE TABLE Market_data_Backtest (
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
                        Amount decimal(19,3);'''
MySQL.Execute_Code(sql_str)
