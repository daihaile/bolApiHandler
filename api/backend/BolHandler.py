import requests
import logging
import time
import json
import pprint as pp
import datetime

class BolHandler():

    
    auth = "XXXX"

    def __init__(self):
        self.CLIENT_ID = "57682479-7dfc-41d1-a05a-cbe9bc2d9270"
        self.CLIENT_SECRET = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        self.BEARER_TOKEN_LOGIN = "https://login.bol.com/token"
        self.URL = "https://api.bol.com/retailer"
        self.BEARER_TOKEN = self.get_bearer_token()
        self.BEARER_TOKEN_EXPIRES = None
        self.tokenTime = datetime.datetime.now()

    def get_bearer_token(self):
        querystring = {"grant_type": "client_credentials"}
        headers = {
            'accept': "application/json",
            'Authorization': "XXXX",
            'Cache-Control': "no-cache",
            'Host': "login.bol.com",
            'Accept-Encoding': "gzip, deflate",
        }
        try:
            response = requests.request(
                "POST", self.BEARER_TOKEN_LOGIN, headers=headers, params=querystring)
            if response.ok:
                token = response.json()["access_token"]
                self.BEARER_TOKEN = token
                logging.info("[Success] Bearer token obtained")
                return token
            else:
                logging.exception("[Fail] " + response.json())
        except requests.RequestException as e:
            logging.exception(e)
        return None


    def get_orders(self):
        orderDict = {}
        url = "/orders"
        auth = "Bearer " + self.BEARER_TOKEN
        page = 1
        query = {"page":str(page)}
        header = {
            'Accept': 'application/vnd.retailer.v3+json',
            'Authorization': auth,
            'Accept-Encoding': "gzip, deflate",
            'Host': "api.bol.com",
        }
        r = requests.get(self.URL + url, headers=header, params= query)
        res = r.json()
        orderDict = res
        while len(res) > 0:
            res = {}
            page = page + 1
            query = {"page":str(page)}
            r = requests.get(self.URL + url, headers=header, params= query)
            res = r.json()
            print(r.status_code)
            if(len(res) > 0):

                if(r.status_code == 429):
                    logging.warning(r.status_code)
                    page = page-1
                    logging.info("resetting page number to try again: Page " + str(page))
                    retry = 301
                    retry = r.headers['Retry-After']
                    logging.warning("retrying GET request in: " + retry)
                    time.sleep(int(retry) + 5)

                elif(r.status_code == 200):
                    print("status code ok, adding another page. Remaining requests: ")
                    print(str(r.headers['X-RateLimit-Remaining']))
                    logging.info("ADDED ANOTHER PAGE")
                    logging.info(r.headers)
                    orderDict['orders'].extend(res['orders'])

        print("got " + str(len(orderDict['orders'])) + " orders")
        return orderDict
    '''
    PATHS

    - /orders
    - /orders/{id}
    - /shipments
    - /shipments/{id}
    - /orders


    '''

    def get_from_bol(self, path):
        auth = "Bearer " + self.BEARER_TOKEN
        header = {
            'Accept': 'application/vnd.retailer.v3+json',
            'content-type':'application/vnd.retailer.v3+json',
            'Authorization': auth,
            'Accept-Encoding': "gzip, deflate",
            'Host': "api.bol.com",
        }
        r = requests.get(self.URL + path, headers=header)
        return r.json()

        r = requests.get(url, headers=header)
        logging.info("Sending request ", r.headers)
        return r.json()

    def get_orderItemIDs_from_orderId(self,orderId):
        orderDict = {}
        orderDict['orderId'] = orderId
        order = self.get_order_by_id(str(orderId))
        if len(order['orderItems']) == 1:
            orderItemId =order['orderItems'][0]['orderItemId']
            orderDict['orderItemId'] = orderItemId
            return orderDict
        elif len(order['orderItems']) > 1:
            orderItemIdList = []
            for i, orderItem in enumerate(order['orderItems']):
                orderItemId =order['orderItems'][i]['orderItemId']
                orderItemIdList.append(orderItemId)

            orderDict['orderItemIds'] = orderItemIdList
            return orderDict
        else: 
            logging.exception("[FAIL] could not find orderItemIds")
            return None

        


    def map_to_dict(self,orderId, transporterCode, trackAndTrace):
        orderDict = self.get_orderItemIDs_from_orderId(orderId)
        if 'orderItemId' in orderDict:
            orderDict['transporterCode'] = transporterCode
            orderDict['trackAndTrace'] = trackAndTrace
            return orderDict
        elif 'orderItemIds' in orderDict:
            print("more than one orderItemId")
            #for i, orderItemId in enumerate(orderDict['orderItemIds']):
            #    print(orderItemId)
        return None



    def put_trackin_to_orderId(self,mergedDF):
        logging.info("[PUT] Adding transport information with")
        logging.info(mergedDF)
        self.get_bearer_token()
        auth = "Bearer " + self.BEARER_TOKEN
        headers = {
            'Accept': "application/vnd.retailer.v3+json",
            'content-type':'application/vnd.retailer.v3+json',
            'Authorization': auth,
            'Cache-Control': "no-cache",
            'Connection': "keep-alive",
            'Host': "api.bol.com",
            'Accept-Encoding': "gzip, deflate",
        }
        mergedDF.loc[:,'sent'] = False
        mergedDF.loc[:,'status'] = None
        mergedDF.loc[:,'description'] = None
        mergedDF.loc[:,'shipmentid'] = None

        
        expireTime = self.tokenTime + datetime.timedelta(minutes = 4)
        for row in mergedDF.iterrows():
            
            currentTime=datetime.datetime.now()
            diff = (expireTime-currentTime).total_seconds()
            if(diff < 100):
                self.BEARER_TOKEN = self.get_bearer_token()
                expireTime = self.tokenTime + datetime.timedelta(minutes = 4)

            

            print()
            print("Send trackingdata to orderId: "+ str(row[1]['orderId']))
            logging.info(row)
            url = self.URL + "/orders/" + row[1]['orderItemId'] + "/shipment"
            data = {
                "shipmentReference": "",
                "transport": {
                    "transporterCode": row[1]['Courier'],
                    "trackAndTrace": row[1]['Tracking Reference']
                }
            }
            # PUT REQUEST ABSENDEN
            pp.pprint(data)
            logging.info("Send trackingdata to orderId: "+ str(row[1]['orderId']))
            r = requests.put(url, data=json.dumps(data),headers=headers)
            pp.pprint(r.text)
            logging.warning(r.text)
            res = r.json()
            mergedDF.at[row[0],['sent']] = True
            mergedDF.at[row[0],['status']] = res.get('status')
            mergedDF.at[row[0],['description']] = res.get('description')
            #print(row)
            #print("Simulated put request to",url,"with",data)
            print()
            time.sleep(1)
        
        print(mergedDF)
        
        return mergedDF




#bol = BolHandler()
