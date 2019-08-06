import json
import os
import pip

def import_or_install(pandas):
    try:
        import__(pandas)
    except ImportError:
        pip.main(['install', pandas])


import pandas as pd
from pandas.io.json import json_normalize

path = r"C:\Users\Mister Sandman\Desktop\Tasks\bolcom track\server\uploads\mijn_openstaande_bestellingen.xls"
class ExcelHandler():
    def __init__(self) -> None:
        super().__init__()

    def read_csv(self,filename):
        #u_cols = ['Client Order Reference','Courier','Tracking Reference']
        df = pd.read_csv(filename, 
            sep='\;',
            engine='python',
            #usecols=u_cols,
            dtype={'Tracking Reference': object})



        #df = df[0].str.split(',', expand=True

        return df
        #return self.filter_dataframe(df,courier="DPD Predict")

    def read_tracking_csv(self,filename):
        u_cols = ['orderId','Courier','Tracking Reference']
        df = pd.read_csv(filename, 
        sep='\;',
        engine='python',
        usecols=u_cols,
        dtype={'Tracking Reference': object})
  
        df.rename(columns={'Client Order Reference':'orderId'},inplace=True)
        return df
        #return self.filter_dataframe(df,courier="DPD Predict")

    def read_excel(self,filename):
        print(filename)
        df = pd.read_excel(filename,index_col=None,na_values=['NA'])
        df.head()

    def save_orders_to_excel(self,orders):
        #df = pd.DataFrame.from_dict(orders['orders'])
        orderDF = json_normalize(orders['orders'], record_path='orderItems', meta=['orderId','dateTimeOrderPlaced'], errors='ignore')
        
        #check for file
        if not os.path.isfile('test.xlsx'):
            orderDF.to_excel('test.xlsx')
        return orderDF

    
    def filter_dataframe(self,df,courier=None,cor=None):
        if courier is not "":
            filtered_df = (df['Courier']==courier)
            print(filtered_df)
            #return filtered_df
        return df
    

