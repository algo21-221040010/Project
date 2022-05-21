"""
创建 MySQLOperation 类
创建 save_order, get_order 来存取order数据库中的数据
"""
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


# host='rm-wz92xxsa5315l05g2so.mysql.rds.aliyuncs.com'
# port=3306
# user='algo76'
# passwd="123456@CUHKSZ"
# db='mfe5210project'
# # 方法实例化
# MySQL = MySQLOperation(host, port, db, user, passwd)

MySQL = MySQLOperation('rm-wz92xxsa5315l05g2so.mysql.rds.aliyuncs.com', 3306, 'mfe5210project', 'algo76', "123456@CUHKSZ")
import datetime
dict = {"datetime":datetime.datetime(2022,1,4,9,30,0),'position_value': 24693.0, 'position': 5, 'direction': 'buy',
        'avg_price': 4938.6, 'volume': 5, 'trade_detail': {0: {'price': 4936.0, 'volume': 1.0}, 1: {'price': 4938.6, 'volume': 1.0},
                                          2: {'price': 4938.8, 'volume': 1.0}, 3: {'price': 4939.6, 'volume': 1.0},
                                          4: {'price': 4940.0, 'volume': 1.0}},}

def save_order_data(dict):
    date_time = dict['datetime']
    position_value = dict['position_value']
    position = dict['position']
    direction = dict['direction']
    avg_price = dict['avg_price']
    volume = dict['volume']
    trade_detail = dict['trade_detail']
    strTemp = ""
    for i in trade_detail:
        priceTemp = trade_detail[i]
        p = str(priceTemp['price'])
        v = str(priceTemp['volume'])
        strTemp += "price%i" %i + ":" + p + " " + "volume%i" %i + ":" + v + ";" + "   "
    print (strTemp)



    sql_str = "INSERT INTO Order_data VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}');".format(date_time,
                                                                                                  position_value,
                                                                                                  position,
                                                                                                  direction,
                                                                                                  avg_price,
                                                                                                  volume,
                                                                                                  strTemp)
    MySQL.Execute_Code(sql_str)


def get_order_data():
    sql_str = 'select * from Order_data'
    results = MySQL.Select_Code(sql_str)
    print(results)



save_order_data(dict)

get_order_data()
