import pandas as pd
import torch
import numpy as np

signal=np.array(torch.load('proj/result.pt'))-1
signal=np.where(signal<0, 0, signal)
for i,_ in enumerate(signal):
    n=len(signal)
    if signal[i]==1 and i+30<n:
        signal[i+30]=-1
    if i==n-1:
        signal[i]=-1


x = pd.read_csv('proj/datetime2202.csv')
x['TradingTime']=pd.to_datetime(x['TradingTime'])
x['signal']=signal

res=dict(zip(x['TradingTime'], x['signal']))
import pickle
with open("signal.pkl", "wb") as tf:
    pickle.dump(res,tf)