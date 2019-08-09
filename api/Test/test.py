import pandas as pd
from pandas.io.json import json_normalize
import numpy as np
import pprint as pp
import os
from csv import Sniffer


def read_tracking_csv( filename):

    sep = ','

    with open(filename,'r') as csvFile:
        dialect = Sniffer().sniff(csvFile.read(30))
        if dialect.delimiter == ';':
            sep = ';'
        elif dialect.delimiter ==',':
            sep = ','

    u_cols = [3,4,5]
    df = pd.read_csv(filename,
                     sep=sep ,
                     header=None,
                     skiprows=1,
                     engine='python',
                     usecols=u_cols,
                     names=['orderId','Courier','Tracking Reference'],
                     dtype={'orderId':str,'Tracking Reference':str}
                     )
    
    df = df[df['orderId'].str.contains(r'^2[0-9]{1,9}$',na=False)]
    df = df[df['Courier'].str.startswith(('DPD','GLS'),na=False)]
    df = df.replace(regex=r'(GLS Paket OVL Berlin|GLS Normalpaket)', value="GLS")
    df = df.replace(regex=r'DPD Predict', value="DPD")
    return df.dropna()


trackDF = read_tracking_csv(r"C:\Users\Mister Sandman\Downloads\MrSandman_Daily_Tracking_CSV.csv")
orders = pd.read_csv(r"C:\Users\Mister Sandman\Desktop\Tasks\bolcom track\server\api\files\orders.csv", dtype=str)

mergedDF = pd.merge(trackDF,orders,how='left')


print(trackDF)
print(orders)
print(mergedDF.iloc[:,0:4])