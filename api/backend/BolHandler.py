import requests
import logging
import time
import json
import pprint as pp

class BolHandler():

    # generated with postman,woops
    auth = "Basic NTc2ODI0NzktN2RmYy00MWQxLWEwNWEtY2JlOWJjMmQ5MjcwOkFNS3NNd1VmclEtcGE0X1FtR0dwZnc4ZFEzQV8xT19vS21PbWJQaWxpZlI4NHBQeHgyY3pXTFR3TzFnRGJ1amI2em9OTkZ2SmxqNTRXaGRvT3NmQmZYSQ=="

    def __init__(self):
        self.CLIENT_ID = "57682479-7dfc-41d1-a05a-cbe9bc2d9270"
        self.CLIENT_SECRET = "AMKsMwUfrQ-pa4_QmGGpfw8dQ3A_1O_oKmOmbPilifR84pPxx2czWLTwO1gDbujb6zoNNFvJlj54WhdoOsfBfXI"
        self.BEARER_TOKEN_LOGIN = "https://login.bol.com/token"
        self.URL = "https://api.bol.com/retailer"
        self.BEARER_TOKEN = self.get_bearer_token()
        self.BEARER_TOKEN_EXPIRES = None

    def get_bearer_token(self):
        querystring = {"grant_type": "client_credentials"}
        headers = {
            'accept': "application/json",
            'Authorization': "Basic NTc2ODI0NzktN2RmYy00MWQxLWEwNWEtY2JlOWJjMmQ5MjcwOkFNS3NNd1VmclEtcGE0X1FtR0dwZnc4ZFEzQV8xT19vS21PbWJQaWxpZlI4NHBQeHgyY3pXTFR3TzFnRGJ1amI2em9OTkZ2SmxqNTRXaGRvT3NmQmZYSQ==",
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
            logging.exception("[FAil] " + e)
        return None


    def get_orders(self):
        self.get_bearer_token()
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
            if(len(res) > 0):
                logging.info("ADDED ANOTHER PAGE")
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
        self.get_bearer_token()
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

    def get_order_by_id(self, id):
        if(is_number(id)):
            id = str(id)
        url = self.URL + "/orders/" + str(id)
        self.get_bearer_token()
        auth = "Bearer " + self.BEARER_TOKEN
        header = {
            'Accept': 'application/vnd.retailer.v3+json',
            'Authorization': auth,
            'Accept-Encoding': "gzip, deflate",
            'Host': "api.bol.com",
        }

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

        for row in mergedDF.iterrows():
            print()
            print("Send trackingdata to orderId: "+ str(row[1]['orderId']))
            logging.info(row)
            url = self.URL + "/orders/" + row[1]['orderItemId'] + "/shipment"
            print(url)
            data = {
                "shipmentReference": "",
                "transport": {
                    "transporterCode": row[1]['Courier'],
                    "trackAndTrace": row[1]['track']
                }
            }
            # PUT REQUEST ABSENDEN
            pp.pprint(data)
            logging.info("Send trackingdata to orderId: "+ str(row[1]['orderId']))
            #r = requests.put(url, data=json.dumps(data),headers=headers)
            #pp.pprint(r.text)
            #logging.warning(r.text)
            time.sleep(1)
            print()
        
        return mergedDF





def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

#pp.pprint(orders)
#print(len(orders['orders']))
#bol.put_trackin_to_orderId("2445845650","GLS","1345057486531")
#bol.put_trackin_to_orderId("2444844710","DPD","01345057485995")


#bol = BolHandler()
