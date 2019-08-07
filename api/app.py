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
    #print(orders)
    #ordersDF = pd.DataFrame.from_dict(orders['orders'])
    #ordersDF.to_csv('rawOrders.csv')
    #excelHandler.save_orders_to_csv(orders)
    
    return render_template('index.html', message="UPLOAD 2 FILES")


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
    mergedDF.replace('GLS Normalpaket','GLS', inplace=True)
    df = bolHandler.put_trackin_to_orderId(mergedDF)
    
    return df.to_json()

@app.route('/uploader', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        trackingFile = request.files['trackingFile']
        ordersFile = request.files['ordersFile']
        if 'trackingFile' not in request.files or 'ordersFile' not in request.files:
            print("No files")
            return render_template('index.html', message="no trackingFile")

        if trackingFile.filename == '':
            return render_template('index.html', message="no file")

        if trackingFile and ordersFile:
            # get dataframe from CSV Upload
            tracking_filename = secure_filename(trackingFile.filename)
            orders_filename = secure_filename(ordersFile.filename)
            trackingFile.save(os.path.join(app.config['UPLOAD_FOLDER'], tracking_filename))
            ordersFile.save(os.path.join(app.config['UPLOAD_FOLDER'], orders_filename))
            tracking_path = app.config['UPLOAD_FOLDER'] + "\\" + tracking_filename
            orders_path = app.config['UPLOAD_FOLDER'] + "\\" + orders_filename
            print(tracking_path)
            print(orders_path)

            # Read Tracking csv file
            trackDF = excelHandler.read_tracking_csv(tracking_path)
            print(trackDF)
            print(trackDF.iloc[0,:])
            
            # get orders from /orders/ for orderItemIds
            #ordersRaw = bolHandler.get_orders()
            #orderItemIdDF = excelHandler.save_orders_to_csv(ordersRaw)

            # Read Orders Excel file for countryCode
            ordersDF = excelHandler.read_order_excel(orders_path)
            
            orders = pd.read_csv(r"C:\Users\Mister Sandman\Desktop\Tasks\bolcom track\server\api\orders.csv", dtype=str, usecols=[
                                 'orderId', 'orderItemId', 'cancelRequest'])
            # print("got orders, merging")
            # mergedDF = mergeDF(orders, trackDF)
            # mergedDF= mergedDF.dropna()
            # print(mergedDF)
            # excelHandler.save_to_csv(mergedDF, 'merged')
            return "test"
            #return render_template('index.html', tables=[mergedDF.to_html(classes='data')], titles=df.columns.values, message='got csv')
            
        else:
            return "errrooooororrrrs"




def addCountryCode(mergedDF, countryCodeDF):
    return None

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
        print(index, " - checking for orderId: ", row.orderId)
        for tat in tatDF2.iterrows():
            # iterate over tracking list
            #logging.info("Comparing {} {}".format(str(row.orderId),tat[1]['orderId']))
            
            #print(row.orderId, tat[1]['orderId'])
            print(tat)
            break


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
