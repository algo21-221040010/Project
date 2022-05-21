from pymysql import *
from sqlalchemy import create_engine
import pandas as pd

host='rm-wz92xxsa5315l05g2so.mysql.rds.aliyuncs.com'
port=3306
user='algo76'
passwd="123456@CUHKSZ"
db='mfe5210project'

conn = connect(host=host,port=port
                ,user=user,passwd=passwd
                ,db=db,charset='utf8')
cursor = conn.cursor()
data = pd.read_csv('202202.csv')
for i in list(range(data.shape[0])):
    sql = "INSERT INTO Market_data_Backtest VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(data.iloc[i,0],data.iloc[i,1],data.iloc[i,2],data.iloc[i,3],data.iloc[i,4],data.iloc[i,5],data.iloc[i,6],data.iloc[i,7],data.iloc[i,8],data.iloc[i,9],data.iloc[i,10],data.iloc[i,11])
    cursor.execute(sql)
    conn.commit()

data =  pd.read_sql("SELECT * FROM `Market_data_Backtest`",con = conn)

print(data)