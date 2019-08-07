import pandas as pd
from pandas.io.json import json_normalize
import pprint as pp
import os


def read_order_excel(filename):
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


filename = r"C:\Users\Mister Sandman\Desktop\Tasks\bolcom track\server\uploads\mijn_openstaande_bestellingen_1.xls"

orders = read_order_excel(filename)
print(orders)
