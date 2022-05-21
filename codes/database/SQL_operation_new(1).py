from pymysql import *
from sqlalchemy import create_engine
import pandas as pd

host='rm-wz92xxsa5315l05g2so.mysql.rds.aliyuncs.com'
port=3306
user='algo76'
passwd="123456@CUHKSZ"
db='algotest'

conn = connect(host=host,port=port
                ,user=user,passwd=passwd
                ,db=db,charset='utf8')
cursor = conn.cursor()

# data = pd.read_csv('C:/Users/jrqh/Desktop/data.csv')
# for i in list(range(data.shape[0])):
#     sql = "INSERT INTO test0508 VALUES ('%s','%s','%s','%s')"%(data.iloc[i,0],data.iloc[i,1],data.iloc[i,2],data.iloc[i,3])
#     cursor.execute(sql)
#     conn.commit()

#sql = "INSERT INTO test0508 VALUES ('%s','%s','%s','%s')"%("111","111","111","111")
# cursor.execute(sql)
# conn.commit()

testData =  pd.read_sql("SELECT * FROM `test0508`",con = conn)
print(testData)

sqlGetPrice = "select LastPrice from test0508  where TradingDate = '20220505' and TradingTime = '30:00.1'"
cursor.execute(sqlGetPrice)
price = cursor.fetchone()
print(price[0])
def toSql(dictVariable, key1 = "",key2 = ""):
    dictVariable[key1]
    sqlStr = "INSERT INTO Order_data VALUES (%s,'24693.0','5','buy','4938.6','5',
' {0: {'price': 4936.0, 'volume': 1.0}, 1: {'price': 4938.6, 'volume': 1.0},
2: {'price': 4938.8, 'volume': 1.0}, 3: {'price': 4939.6, 'volume': 1.0}, 4: {'price': 4940.0, 'volume': 1.0}}')"


conn.close()