from flask import Flask
from flask import request
from flask import send_file


import json
import pandas as pd
import os
from werkzeug.utils import secure_filename
from flask_restful import Api
from flask import render_template

import logging

# from backend.BolHandler import BolHandler
from resources.landing import Landing
from backend.excelHandler import ExcelHandler
from backend.BolHandler import BolHandler

# set FLASK_ENV=development
# python -m flask run


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = r"C:\Users\Mister Sandman\Desktop\Tasks\bolcom track\server\uploads"
api = Api(app)

logging.basicConfig(format='%(asctime)s %(message)s',
                    filename="NEW LOG.log",
                    level=logging.DEBUG)


# bolHandler = BolHandler()
excelHandler = ExcelHandler()
bolHandler = BolHandler()
api.add_resource(Landing, '/landing',
                 resource_class_kwargs={'handler': excelHandler})


@app.route('/')
def test():
    #orders = bolHandler.get_orders()

    # excelHandler.save_orders_to_csv(orders)
    return render_template('index.html', message="saved orders to csv file")


@app.route('/bol', methods=['GET', 'POST'])
def get_from_bol():
    path = request.form['path']
    r = bolHandler.get_from_bol(path)
    r2 = json.dumps(r, sort_keys=False, indent=4, separators=(',', ': '))
    return render_template('index.html', order=r2)


@app.route('/put', methods=['GET'])
def putBol():
    mergedDF = pd.read_csv(
        r"C:\Users\Mister Sandman\Desktop\Tasks\bolcom track\server\api\merged.csv", dtype=str) 
    bolHandler.put_trackin_to_orderId(mergedDF)
    
    return mergedDF.to_json()

@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if 'file' not in request.files:
            print("No file part")
            return render_template('index.html', message="no file")

        if file.filename == '':
            return render_template('index.html', message="no file")

        if file:
            # get dataframe from CSV Upload
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            path = app.config['UPLOAD_FOLDER'] + "\\" + filename
            print(path)

            df = excelHandler.read_tracking_csv(path)
            df.rename(
                columns={'Client Order Reference': 'orderId'}, inplace=True)

            #ordersRaw = bolHandler.get_orders()
            # excelHandler.save_orders_to_csv(ordersRaw)
            # excelHandler.save_orders_to_excel(ordersRaw)
            orders = pd.read_csv(r"C:\Users\Mister Sandman\Desktop\Tasks\bolcom track\server\api\orders.csv", dtype=str, usecols=[
                                 'orderId', 'orderItemId', 'cancelRequest'])

            # filter Dataframe with bol API get /orders/
            #  filter_df(orders, df)
            mergedDF = mergeDF(orders, df)
            print(mergedDF.dropna())
            # return html_from_df
            excelHandler.save_to_csv(mergedDF, 'merged')

            return render_template('index.html', tables=[mergedDF.to_html(classes='data')], titles=df.columns.values, message='got csv')

        else:
            return "errrooooororrrrs"


def filter_df(orders, tat_df):

    logging.info("GOT ORDERS")

    # ADD TRACKING TO OBJECTS
    dup_df = tat_df[tat_df.duplicated()]

    order_DF = excelHandler.save_orders_to_excel(orders)
    order_DF.drop(['ean', 'cancelRequest', 'quantity', 'dateTimeOrderPlaced'],
                  axis=1, inplace=True)
    logging.info("SAVING ORDERS")

    #mergedDF = pd.merge(tat_df,order_DF,on=['Client Order Reference'],how='right')
    # print(mergedDF


def mergeDF(ordersDF, tatDF):
    ordersDF.loc[:, 'Courier'] = None
    ordersDF.loc[:, 'track'] = None

    # ADD USED FLAG TO TRACKINGCSV
    tatDF['used'] = False

    ordersDF2 = ordersDF
    tatDF2 = tatDF
    logging.info(tatDF2.iterrows())
    count = 0

    print("starting DF")
    print(ordersDF)

    for index, row in ordersDF2.iterrows():
        #print(index, " - checking for orderId: ", row.orderId)
        for tat in tatDF2.iterrows():
            # iterate over tracking list
            #logging.info("Comparing {} {}".format(str(row.orderId),tat[1]['orderId']))
            if(row.orderId == tat[1]['orderId']):
                if(row.cancelRequest == 'True'):
                    print("cancel request on {}, dropping order".format(row.orderId))
                    break
                count = count+1
                if(tat[1]['used'] == False):
                    print("free trackingnumber ",
                          tat[1].orderId, tat[1]['Tracking Reference'])
                    ordersDF.at[index, 'Courier'] = tat[1]['Courier']
                    ordersDF.at[index, 'track'] = tat[1]['Tracking Reference']
                    tatDF.at[tat[0], 'used'] = True
                    break  # break out of tat loop
                elif(tat[1]['used'] == True):
                    print("Tracking number {} used already, searching for free tracking number with id {}".format(
                        tat[1]['Tracking Reference'], tat[1].orderId))

    logging.info("Found {} matching Ids".format(count))
    print("Found {} matching Ids".format(count))
    print()
    ordersDF.fillna(value=pd.np.nan, inplace=True)
    ordersDF.dropna(inplace=True)
    print("FINAL DATAFRAME")
    logging.info(ordersDF)
    print()

    print("Tracking Dataframe")
    print(tatDF)
    return ordersDF


if __name__ == '__main__':
    app.run('localhost', debug=True, port=5050)
