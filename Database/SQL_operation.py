# database
# mysql -h rm-wz92xxsa5315l05g2so.mysql.rds.aliyuncs.com -u algo76 -p

from pymysql import *
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

import pandas as pd
host='rm-wz92xxsa5315l05g2so.mysql.rds.aliyuncs.com'
port=3306
user='algo76'
passwd="123456@CUHKSZ"
db='algotest'
# 方法实例化
MySQL = MySQLOperation(host, port, db, user, passwd)

#建表
sql_str = '''CREATE TABLE Test (
                        secu_code CHAR(20),
                        hs_code CHAR(20),
                        secu_abbr CHAR(20),
                        chi_name CHAR(40),
                        secu_market CHAR(20), 
                        listed_state CHAR(20),
                        listed_sector CHAR(20),
                        updatetime CHAR(20));'''
MySQL.Execute_Code(sql_str)

# 插入操作代码
sql_str = '''
INSERT INTO Test
(`secu_code`,`hs_code`,`secu_abbr`,`chi_name`,`secu_market`,`listed_state`,`listed_sector`,`updatetime`)
VALUES
('000001','000001.SZ','平安银行','平安银行股份有限公司','深圳证券交易所','上市',
'主板','2021-10-25 20:15:55');
'''
MySQL.Execute_Code(sql_str)

# 查询数据
sql_str = 'select * from Test'
results = MySQL.Select_Code(sql_str)
print(results)

sql_str = '''
select chi_name from Test where secu_code='000001'
'''
results = MySQL.Select_Code(sql_str)
print(results)


