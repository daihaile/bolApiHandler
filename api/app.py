from flask import Flask
from flask import request
from flask import send_file

import numpy as np
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
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
app.config['DOWNLOAD_FOLDER'] = os.path.join(app.root_path, 'files')
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
    print(bolHandler.BEARER_TOKEN)
    #orders = bolHandler.get_orders()
    # print(orders)
    #ordersDF = pd.DataFrame.from_dict(orders['orders'])
    # ordersDF.to_csv('rawOrders.csv')
    # excelHandler.save_orders_to_csv(orders,app.config['DOWNLOAD_FOLDER'])

    return render_template('index.html', message="UPLOAD 2 FILES")


@app.route('/getMerged')
def getMeged():
    path = app.config['DOWNLOAD_FOLDER']
    file = os.path.join(path, 'merged.csv')
    print(pd.read_csv(file))
    print(os.path.join(path, 'merged.csv'))

    return send_file(file, as_attachment=True, attachment_filename='merged.csv')


@app.route('/getShipped')
def getSHipped():
    path = app.config['DOWNLOAD_FOLDER']
    file = os.path.join(path, 'shipped.csv')
    print(os.path.join(path, 'shipped.csv'))

    return send_file(file, as_attachment=True, attachment_filename='shipped.csv')


@app.route('/bol', methods=['GET', 'POST'])
def get_from_bol():
    path = request.form['path']
    r = bolHandler.get_from_bol('/orders/' + path)
    r2 = json.dumps(r, sort_keys=False, indent=4, separators=(',', ': '))
    return render_template('index.html', order=r2)


@app.route('/put', methods=['GET'])
def putBol():
    mergedDF = pd.read_csv(os.path.join(
        app.config['DOWNLOAD_FOLDER'], 'merged.csv'), dtype=str)
    df = bolHandler.put_trackin_to_orderId(mergedDF)
    excelHandler.save_to_csv(df,'shipped.csv',app.config['DOWNLOAD_FOLDER'])
    return render_template('index.html', uploaded_tables=[mergedDF.to_html(classes='data')], uploaded_titles=mergedDF.columns.values, message='UPLOADED')


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
            trackingFile.save(os.path.join(
                app.config['UPLOAD_FOLDER'], tracking_filename))
            ordersFile.save(os.path.join(
                app.config['UPLOAD_FOLDER'], orders_filename))
            tracking_path = app.config['UPLOAD_FOLDER'] + \
                "\\" + tracking_filename
            orders_path = app.config['UPLOAD_FOLDER'] + "\\" + orders_filename

            # Read Tracking csv file
            trackDF = excelHandler.read_tracking_csv(tracking_path)

            # get orders from /orders/ for orderItemIds
            ordersRaw = bolHandler.get_orders()
            orderItemIdDF = excelHandler.save_orders_to_csv(
               ordersRaw, app.config['DOWNLOAD_FOLDER'])
            orders = orderItemIdDF

            #orders = pd.read_csv(r"C:\Users\Mister Sandman\Desktop\Tasks\bolcom track\server\api\files\orders.csv", dtype=str)

            # Read Orders Excel file for countryCode
            countryDF = excelHandler.read_order_excel(orders_path)
            print("country DF")
            print(countryDF)
            # Adding countryCode to TrackDF
            orderIdwithCountryDF = addCountryCode(orders, countryDF)
            print("order with country DF")
            print(orderIdwithCountryDF)

            mergedDF = mergeDF(orderIdwithCountryDF, trackDF)
            mergedDF = mergedDF.dropna()

            print("TrackingDF")
            print(trackDF)
            print("Merged Dataframe with countryCode")
            print(mergedDF)

            excelHandler.save_to_csv(
                mergedDF, 'merged.csv', app.config['DOWNLOAD_FOLDER'])
            return render_template('index.html', tables=[mergedDF.to_html(classes='data')], titles=mergedDF.columns.values, message='got csv')

        else:
            return "errrooooororrrrs"


def addCountryCode(ordersDF, countryDF):
    # print(trackDF)
    countryDF.rename(columns={"bestelnummer": "orderId",
                              "land_verzending": "countryCode"}, inplace=True)
    result = pd.merge(ordersDF, countryDF, on='orderId', how='left')
    return result


def mergeDF(ordersDF, tatDF):
    ordersDF.loc[:, 'Courier'] = 'EMPTY'
    ordersDF.loc[:, 'Tracking Reference'] = 'EMPTY'

    # ADD USED FLAG TO TRACKINGCSV
    tatDF['used'] = False
    tatDF['description'] = "not in /orders/"

    ordersDF2 = ordersDF
    count = 0
    stop = False
    cancelRequests = []

    #print("starting DF")
    # print(ordersDF)

    for index, row in ordersDF.iterrows():
        print(index, " - checking for order ", row.orderId, row.cancelRequest)
        if(row.cancelRequest == 'True' or row.cancelRequest == 'true' or row.cancelRequest == True):
            print("cancel request on {}, dropping order".format(row.orderId))
            cancelRequests.append(row)
            stop = True
        else:
            stop = False

        for tat in tatDF.iterrows():
            # iterate over tracking list
            #print(row.orderId,tat[1]['orderId'],tat[1]['Tracking Reference'],tat[1]['Courier'])
            if(row.orderId == tat[1]['orderId']):

                if stop:
                    print('setting',tatDF.at[tat[0], 'description'], 'to ', 'cancel request')
                    tatDF.at[tat[0], 'description'] = 'cancel request'
                    break
                print("[Match]")
                count = count+1
                if(tat[1]['used'] == False):
                    print("free trackingnumber ",
                          tat[1].orderId, tat[1]['Tracking Reference'], " - setting used=True")
                    #ordersDF.at[index, 'Courier'] = tat[1]['Courier']
                    print("converting ", row.countryCode, tat[1]['Courier'])
                    ordersDF.at[index, 'Courier'] = convertCourier(row.countryCode, tat[1]['Courier'])
                    #ordersDF.at[index, 'Courier'] = tat[1]['Courier']
                    ordersDF.at[index, 'Tracking Reference'] = tat[1]['Tracking Reference']
                    tatDF.at[tat[0], 'used'] = True
                    break  # break out of tat loop
                elif(tat[1]['used'] == True):
                    print("Tracking number {} used already, searching for free tracking number with id {}".format(
                        tat[1]['Tracking Reference'], tat[1].orderId))
                    print(row)
                    print(int(row.quantity))
                    if(int(row.quantity) > 1):
                        print('quantity > 1')
                        tatDF.at[tat[0], 'description'] = 'quantity > 1'
                    


    logging.info("Found {} matching Ids".format(count))
    print("Found {} matching Ids. {} cancel requests".format(
        count, len(cancelRequests)))

    canceledDF = pd.DataFrame(cancelRequests, columns=ordersDF.columns)
    excelHandler.save_to_csv(canceledDF, 'canceled.csv',
                             app.config['DOWNLOAD_FOLDER'])
    excelHandler.save_to_csv(tatDF, 'tracking.csv',app.config['DOWNLOAD_FOLDER'])
    print()
    print()

    ordersDF = ordersDF.replace(to_replace='EMPTY', value=np.nan)
    ordersDF.fillna(value=pd.np.nan, inplace=True)
    ordersDF.dropna(inplace=True)
    logging.info(ordersDF)
    return ordersDF


def convertCourier(countryCode, courier):
    if(countryCode == 'BE' and courier == 'DPD'):
        return 'DPD-BE'
    elif(countryCode == 'NL' and courier == 'DPD'):
        return 'DPD-NL'
    elif(courier == 'GLS'):
        return 'GLS'
    else:
        return None


if __name__ == '__main__':
    app.run(host='0.0.0.0',port='8080')
