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
data = pd.read_csv('202202bidask.csv')
for i in list(range(data.shape[0])):
    sql = "INSERT INTO Market_data_Trade VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(data.iloc[i,0],data.iloc[i,1],data.iloc[i,2],data.iloc[i,3],data.iloc[i,4],data.iloc[i,5],data.iloc[i,6],data.iloc[i,7],data.iloc[i,8],data.iloc[i,9],data.iloc[i,10],data.iloc[i,11],data.iloc[i,12],data.iloc[i,13],data.iloc[i,14],data.iloc[i,15],data.iloc[i,16],data.iloc[i,17],data.iloc[i,18],data.iloc[i,19],data.iloc[i,20],data.iloc[i,21],data.iloc[i,22],data.iloc[i,23],data.iloc[i,24],data.iloc[i,25],data.iloc[i,26],data.iloc[i,27],data.iloc[i,28],data.iloc[i,29],data.iloc[i,30],data.iloc[i,31],data.iloc[i,32],data.iloc[i,33],data.iloc[i,34],data.iloc[i,35],data.iloc[i,36],data.iloc[i,37],data.iloc[i,38],data.iloc[i,39],data.iloc[i,40],data.iloc[i,41],data.iloc[i,42],data.iloc[i,43],data.iloc[i,44],data.iloc[i,45],data.iloc[i,46],data.iloc[i,47],data.iloc[i,48],data.iloc[i,49],data.iloc[i,50],data.iloc[i,51],data.iloc[i,52],data.iloc[i,53],data.iloc[i,54],data.iloc[i,55],data.iloc[i,56],data.iloc[i,57],data.iloc[i,58],data.iloc[i,59],data.iloc[i,60],data.iloc[i,61])
    cursor.execute(sql)
    conn.commit()
# data =  pd.read_sql("SELECT * FROM `Market_data_Backtest`",con = conn)
# print(data)