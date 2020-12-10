import logging
import time
import requests
import hashlib


#constructor
def __init__(context):
    context.openHIMAuthenticationUrl = context.configData["openHIM"]["baseUrl"] + '/authenticate/root@openhim.org'
    context.openHIMTransactionsURL = context.configData["openHIM"]["baseUrl"] + '/transactions'
    context.isFHIRTransaction = True
       
def checkOpenHIMTransaction(context):  
    if (context.currObs.isSentinelEvent == False) :     
        return   
    logging.info("Confirm transactions sent to OpenHIM are successful")
    index = 0 
    successful = False   
    while index < 5:
        index += 1           
        rHeaders = getOpenHIMHeaders(context)
        response = requests.get(context.openHIMTransactionsURL, headers=rHeaders, verify=False)
        data = response.json()  
        if (response is not None ) :
            response.close()         
        if (response.status_code > 201) :            
            continue 
        
        transactionData = data[0]        
        #transactionTime = datetime.strptime(transaction['request']['timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if (str(transactionData['status']) !='Successful') :
            logging.info("There are some transactions that are still not complete. we will wait for 15 seconds and check for status")                                                                
            time.sleep(10)
            continue
        else :              
            successful = True  
            if (data[0]['request']['path'].find('/xdsrepository')  != -1) :
                context.isFHIRTransaction = False               
            break   
    assert (successful)


def getOpenHIMHeaders (context):
    response = None
    count = 0
    while (count < 10) :
        count += 1
        try :
            response = requests.get(context.openHIMAuthenticationUrl, verify=False) 
            break; 
        except :
            time.sleep(10) 
            
    data = response.json() 
    response.close()
    passhash = hashlib.sha512((data['salt'] + "openhim").encode()).hexdigest()
    token = hashlib.sha512((passhash + data['salt'] + data['ts']).encode()).hexdigest()

    ts = str(data['ts'])
    salt = str(data['salt'])
    return {
        "auth-username":"root@openhim.org",
        "auth-ts": ts, 
        "auth-salt": salt,
        "auth-token":token,
        "Connection":"close"
    }


def deleteOldOpenHIMTransactions(context): 
    logging.info ('Starting cleaning of previous run OpenHIM data')           
    rHeaders = getOpenHIMHeaders(context)
    response = requests.get(context.openHIMTransactionsURL, headers=rHeaders, verify=False)
    data = response.json()
    for transaction in data:
        try :
            trans_id = transaction['_id']
            rHeaders = getOpenHIMHeaders(context)        
            response = requests.delete(context.openHIMTransactionsURL + "/" + trans_id, headers=rHeaders, verify=False)        
            response.close()
        except :
            #time for openhim to close connection
            time.sleep(8)

