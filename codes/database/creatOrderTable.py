"""
创建 Order_data 表
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


host='rm-wz92xxsa5315l05g2so.mysql.rds.aliyuncs.com'
port=3306
user='algo76'
passwd="123456@CUHKSZ"
db='mfe5210project'
# 方法实例化
MySQL = MySQLOperation(host, port, db, user, passwd)

# 建表
sql_str = '''CREATE TABLE Order_data (
                        date_time TIMESTAMP(6),
                        position_value FLOAT(40),
                        position FLOAT(40),
                        direction CHAR(20),
                        avg_price FLOAT(40),
                        volume INT(20),
                        trade_detail CHAR(255));'''
MySQL.Execute_Code(sql_str)

# 插入操作代码
sql_str = '''
INSERT INTO Order_data
(`date_time`,`position_value`,`position`,`direction`,`avg_price`,`volume`,`trade_detail`)
VALUES
('2022-01-04 09:30:00.400000','24693.0','5','buy','4938.6','5', '001');
'''
MySQL.Execute_Code(sql_str)

## # 查询数据
sql_str = 'select * from Order_data'
results = MySQL.Select_Code(sql_str)
print(results)