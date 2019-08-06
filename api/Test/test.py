import pandas as pd


print("Test")

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




'''


for orderId in uniqueDF['orderId']:
    print("checking for: " + orderId)
    for i in range(len(tatDF['orderId'])):
        if tatDF['orderId'][i] == orderId:
            uniqueDF
            print(s)
'''

