from flask import Flask
from flask import request
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
    orders = bolHandler.get_orders()
    
    excelHandler.save_orders_to_excel(orders)
    return render_template('index.html', message="saved orders to excel file")

    
@app.route('/bol', methods=['GET','POST'])
def get_from_bol():
    path= request.form['path']
    r = bolHandler.get_from_bol(path)
    r2 = json.dumps(r, sort_keys = False, indent = 4, separators = (',', ': '))
    return render_template('index.html',order= r2)


@app.route('/singleOrder')
def singleOrder():
    path = app.config['UPLOAD_FOLDER'] + "\\" + "mijn_openstaande_bestellingen.xls"
    logging.info(path)
    df = excelHandler.read_csv(path)
    order = bolHandler.get_order_by_id("/orders",2444895940)

    # filter Dataframe with bol API get /orders/
    #filter_df(df)
    return render_template('index.html',order=order)

@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if 'file' not in request.files:
            print("No file part")
            return render_template('index.html',message="no file")

        if file.filename == '':
            return render_template('index.html', message="no file")

        if file:
            # get dataframe from CSV Upload
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            path = app.config['UPLOAD_FOLDER'] + "\\" +  filename
            print(path)
            df = excelHandler.read_tracking_csv(path)

            # filter Dataframe with bol API get /orders/
            filter_df(df)
            # return html_from_df
            return render_template('index.html',tables=[df.to_html(classes='data')],titles=df.columns.values,message='got csv')

        else:
            return "errrooooororrrrs"
        
def filter_df(tat_df):
    orders = bolHandler.get_orders()
    logging.info("GOT ORDERS")
    order_DF = excelHandler.save_orders_to_excel(orders)
    order_DF.drop(['ean','cancelRequest','quantity','dateTimeOrderPlaced'],
        axis=1, inplace=True)
    logging.info("SAVING ORDERS")
    
    order_DF.rename(columns={'orderId':'Client Order Reference'},inplace=True)

    #mergedDF = pd.merge(tat_df,order_DF,on=['Client Order Reference'],how='right')
    #print(mergedDF)

    print(order_DF)



if __name__ == '__main__':
    app.run('localhost', debug=True)
