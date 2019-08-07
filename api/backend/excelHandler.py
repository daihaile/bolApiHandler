from pandas.io.json import json_normalize
import pandas as pd
import json
import os
import pip


def import_or_install(pandas):
    try:
        import__(pandas)
    except ImportError:
        pip.main(['install', pandas])


path = r"C:\Users\Mister Sandman\Desktop\Tasks\bolcom track\server\uploads\mijn_openstaande_bestellingen.xls"


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
                           encoding='utf-8'
                           )
        df = df.replace(regex=r'^Belgi.$', value="BE")
        df = df.replace(regex=r'Nederland', value="NL")
        return df

    def read_tracking_csv(self, filename):
        u_cols = [3,4,5]

        df = pd.read_csv(filename,
                         sep='\,',
                         header=None,
                         skiprows=1,
                         engine='python',
                         usecols=u_cols,
                         names=['orderId','Courier','Tracking Reference'],
                         dtype=str)
        return df

        # return self.filter_dataframe(df,courier="DPD Predict")

    def read_excel(self, filename):
        print(filename)
        df = pd.read_excel(filename, index_col=None, na_values=['NA'])
        df.head()

    def save_orders_to_excel(self, orders):
        #df = pd.DataFrame.from_dict(orders['orders'])
        orderDF = json_normalize(orders['orders'], record_path='orderItems', meta=[
                                 'orderId', 'dateTimeOrderPlaced'], errors='ignore')

        # check for file
        if not os.path.isfile('test.xlsx'):
            orderDF.to_excel('test.xlsx')
        return orderDF

    def save_orders_to_csv(self, orders):
        #df = pd.DataFrame.from_dict(orders['orders'])

        orderDF = json_normalize(orders['orders'], record_path='orderItems', meta=[
                                 'orderId', 'dateTimeOrderPlaced'], errors='ignore')

        # check for file
        if os.path.isfile('orders.csv'):
            os.remove('orders.csv')
        if not os.path.isfile('orders.csv'):
            orderDF.to_csv('orders.csv', index=False)
        return orderDF

    def filter_dataframe(self, df, courier=None, cor=None):
        if courier is not "":
            filtered_df = (df['Courier'] == courier)
            print(filtered_df)
            # return filtered_df
        return df

    def save_to_csv(self, data, name):
        if not os.path.isfile(str(name) + '.csv'):
            data.to_csv(str(name) + '.csv', index=False)

    def processTrackingCSV(self, data):
        return None
