import pandas as pd
from pandas.io.json import json_normalize
import pprint as pp

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
      "cancelRequest": False,
      "fulfilmentMethod": "FBR",
      "selectedDeliveryWindow": {
        "date": "2018-01-01",
        "start": "13:00:00",
        "end": "13:00:00"
      }
    }
  ]
}



ordersDF = json_normalize(orders, record_path='orderItems', meta=['orderId','dateTimeOrderPlaced','customerDetails'], errors='ignore')
#orderItemIds = json_normalize(data=orders)
#orderDF = json_normalize(orderItemIds, record_path='orderItems', meta=['orderId','customerDetails.shipmentDetails.countryCode'], errors='ignore')
#pp.pprint(orderItemIds['customerDetails.billingDetails.deliveryPhoneNumber'])
pp.pprint(ordersDF)
