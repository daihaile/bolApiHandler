import pandas as pd
from pandas.io.json import json_normalize

print("Test")


orders = {
  "orderId": "4123456789",
  "dateTimeOrderPlaced": "2017-02-09T12:39:48+01:00",
  "customerDetails": {
    "shipmentDetails": {
      "salutationCode": "02",
      "firstName": "Billie",
      "surName": "Jansen",
      "streetName": "Dorpstraat",
      "houseNumber": "1",
      "houseNumberExtended": "B",
      "addressSupplement": "Lorem Ipsum",
      "extraAddressInformation": "Apartment",
      "zipCode": "1111 ZZ",
      "city": "Utrecht",
      "countryCode": "NL",
      "email": "billie@verkopen.bol.com",
      "company": "bol.com",
      "vatNumber": "NL999999999B99",
      "deliveryPhoneNumber": "012123456"
    },
    "billingDetails": {
      "salutationCode": "02",
      "firstName": "Billie",
      "surName": "Jansen",
      "streetName": "Dorpstraat",
      "houseNumber": "1",
      "houseNumberExtended": "B",
      "addressSupplement": "Lorem Ipsum",
      "extraAddressInformation": "Apartment",
      "zipCode": "1111 ZZ",
      "city": "Utrecht",
      "countryCode": "NL",
      "email": "billie@verkopen.bol.com",
      "company": "bol.com",
      "vatNumber": "NL999999999B99",
      "deliveryPhoneNumber": "012123456"
    }
  },
  "orderItems": [
    {
      "orderItemId": "2012345678",
      "offerReference": "BOLCOM00123",
      "ean": "0000007740404",
      "title": "Product Title",
      "quantity": 10,
      "offerPrice": 27.95,
      "transactionFee": 5.18,
      "latestDeliveryDate": "2017-02-10",
      "offerCondition": "NEW",
      "cancelRequest": false,
      "fulfilmentMethod": "FBR",
      "selectedDeliveryWindow": {
        "date": "2018-01-01",
        "start": "13:00:00",
        "end": "13:00:00"
      }
    }
  ]
}



ordersDF = json_normalize(orders, record_path='orderItems', meta=['orderId','dateTimeOrderPlaced'], errors='ignore')

print(ordersDF)

'''

ordersDF = pd.read_csv(r"C:\Users\Mister Sandman\Desktop\Tasks\bolcom track\server\api\Test\orders.csv",dtype=str, usecols=['orderId','orderItemId'])

tatDF= pd.read_csv(r"C:\Users\Mister Sandman\Desktop\Tasks\bolcom track\server\api\Test\boltracking.csv",sep=';',usecols=['orderId','Tracking Reference','Courier'] ,dtype=str)

#https://stackoverflow.com/questions/14657241/how-do-i-get-a-list-of-all-the-duplicate-items-using-pandas-in-python


ordersDF.loc[:,'Courier'] = None
ordersDF.loc[:,'track'] = None

#ADD USED FLAG TO TRACKINGCSV
tatDF['used'] = False

ordersDF2 = ordersDF
tatDF2 = tatDF

for index,row in ordersDF2.iterrows():
    print(index, " - checking for orderId: ", row.orderId)
    for tat in tatDF2.iterrows():
        # iterate over tracking list
        if(row.orderId == tat[1]['orderId']):
            if(tat[1]['used'] == False):
                print("free trackingnumber ",tat[1].orderId, tat[1]['Tracking Reference'])
                ordersDF.at[index,'Courier'] = tat[1]['Courier']
                ordersDF.at[index,'track'] = tat[1]['Tracking Reference']
                tatDF.at[tat[0],'used'] = True
                break #break out of tat loop
            elif(tat[1]['used'] == True):
                print("Tracking number {} used already, searching for free tracking number with id {}".format(tat[1].orderId, tat[1]['Tracking Reference']))
            
    print()


print()
print("FINAL DATAFRAME")
print(ordersDF)

#print(ordersDF)






for orderId in uniqueDF['orderId']:
    print("checking for: " + orderId)
    for i in range(len(tatDF['orderId'])):
        if tatDF['orderId'][i] == orderId:
            uniqueDF
            print(s)
'''

