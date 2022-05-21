import pymysql
# create_engine('mysql+pymysql://用户名:密码@主机/库名?charset=utf8')
from sqlalchemy import create_engine
import os
host='rm-wz92xxsa5315l05g2so.mysql.rds.aliyuncs.com'
port = 3306
user='algo76'
password="123456@CUHKSZ"
database='algotest'
engine = create_engine('mysql+pymysql://{0}:{1}@{2}:{3}/{4}?charset=utf8'.format(user
                                                                         ,password
                                                                         ,host
                                                                         ,port
                                                                         ,database))

import pandas as pd
# 定义需要写入的数据，DataFrame格式
# df = pd.DataFrame([['000001','000001.SZ','平安银行','平安银行股份有限公司'
#                       ,'深圳证券交易所','上市','主板','2021-10-25 20:12:55'],
#                    ['000002','000002.SZ','万 科Ａ','万科企业股份有限公司'
#                     ,'深圳证券交易所','上市','主板','2021-10-25 20:12:55']])
# # 列名赋值
# df.columns = ['secu_code','hs_code', 'secu_abbr', 'chi_name'
#                 , 'secu_market', 'listed_state','listed_sector','updatetime']
#
#
# # 写入数据库
# df.to_sql(name='stock', con=engine, if_exists='append')

os.chdir(r'D:\Coding\Project\Database')
df2 = pd.read_csv('data.csv')
df2.to_sql(name='test_data', con=engine, if_exists='append')


