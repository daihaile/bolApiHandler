from pandas.io.json import json_normalize
import pandas as pd
import numpy as np
import json
import os
import pip
from csv import Sniffer


def import_or_install(pandas):
    try:
        import__(pandas)
    except ImportError:
        pip.main(['install', pandas])

class ExcelHandler():
    def __init__(self) -> None:
        super().__init__()

    def read_csv(self, filename):
        df = pd.read_csv(filename,
                         sep='\;',
                         engine='python',
                         # usecols=u_cols,
                         dtype=str)
        return df

    def read_order_excel(self, filename):
        u_cols = ['bestelnummer', 'land_verzending']
        df = pd.read_excel(filename,
                           dtype=str,
                           header=2,
                           usecols=u_cols,
                           encoding='utf-8',
                           na_values=['NA'],
                           )

        #df.rename(columns={"bestelnummer":"orderId","land_verzending":"countryCode"})

        df = df.replace(regex=r'^Belgi.$', value="BE")
        df = df.replace(regex=r'Nederland', value="NL")
        return df

    def read_tracking_csv(self, filename):

        sep = ','

        with open(filename,'r') as csvFile:
            dialect = Sniffer().sniff(csvFile.read(30))
            filedata = csvFile.read()
            if dialect.delimiter == ';':
                sep = ';'
            elif dialect.delimiter ==',':
                sep = ','

        filedata = filedata.replace(";",",")

        with open(filename, 'w') as csvFile:
            csvFile.write(filedata)

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
        df = df[df['Courier'].str.startswith(('DPD','GLS','\"GLS'),na=False)]
        df = df.replace(regex=r'(GLS Paket OVL Berlin|GLS Normalpaket|GLS Paket Megaflex Guben|GLS letter box|GLS Paket bis 31,5kg DE )', value="GLS")
        df = df.replace(regex=r'DPD Predict', value="DPD")
        return df.dropna()


    def read_excel(self, filename):
        print(filename)
        df = pd.read_excel(filename, index_col=None, na_values=['NA'])
        df.head()

    def save_orders_to_excel(self, orders,path):
        file = os.path.join(path, 'orders.xlsx')

        orderDF = json_normalize(orders['orders'], record_path='orderItems', meta=[
                                 'orderId', 'dateTimeOrderPlaced'], errors='ignore')

        # check for file
        if not os.path.isfile(file):
            orderDF.to_excel(file)
        return orderDF

    def save_orders_to_csv(self, orders,path):
        file = os.path.join(path, 'orders.csv')

        orderDF = json_normalize(orders['orders'], record_path='orderItems', meta=[
                                 'orderId', 'dateTimeOrderPlaced'], errors='ignore')

        # check for file
        if os.path.isfile(file):
            os.remove(file)
        if not os.path.isfile(file):
            orderDF.to_csv(file, index=False)
        return orderDF

    def save_to_csv(self, data, name ,path):
        file = os.path.join(path,name)
        if os.path.isfile(file):
            os.remove(file)
            data.to_csv(file, index=False)
        if not os.path.isfile(file):
            print("Saved file:" + name)
            data.to_csv(file, index=False)

    def processTrackingCSV(self, data):
        return None

if __name__ == "__main__":
    e = ExcelHandler()
    df = e.read_tracking_csv("C:\\Users\\Mister Sandman\\Desktop\MrSandman_Daily_Tracking_CSV.csv")
    print(df)