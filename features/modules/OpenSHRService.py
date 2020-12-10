import logging
import time
import requests
import os
import json

   
#constructor
def __init__(context):        
    context.shrPatientLkUrl = context.configData["openSHR"]["baseUrl"] + '/ws/rest/v1/patient?q='
    context.shrPersonUrl = context.configData["openSHR"]["baseUrl"] + '/ws/rest/v1/person/'
    context.shrObsUrl = context.configData["openSHR"]["baseUrl"] + '/ws/rest/v1/obs?patient='
    context.shrPatientUrl = context.configData["openSHR"]["baseUrl"] + '/ws/rest/v1/patient/' 

       
def checkShrPerson(context):
    #check person data exists
    logging.info("Check SHR has Patient record for Patient - " + context.currPatient.givenName)
    count = 0 
    isSuccessful = False
    while (count < 5 and isSuccessful == False) :        
        response = requests.get(context.shrPatientLkUrl + context.currPatient.givenName, headers={'Connection':'close'}, auth=(context.configData["openSHR"]["username"], context.configData["openSHR"]["password"]))
        if (response.status_code > 204) :
            time.sleep(5)
            continue
        else :
            isSuccessful = True
            data = response.json() 
            try :
                assert (len (data['results']) == 1)    
            except AssertionError :
                logging.info("EMPI could be returning 2 rows - \n" + str(data))
                
            context.currPatient.shrPatientUUID = data['results'][-1]['uuid']           
            break
        count += 1
        response.close()         
    assert (isSuccessful)


def checkShrObs(context): 
    logging.info("Confirm SHR has related Obs records for the Patient - " + context.currPatient.givenName)
    count = 0 
    isSuccessful = False
    while (count < 5 and isSuccessful == False) :
        count += 1
        response = requests.get(context.shrObsUrl + context.currPatient.shrPatientUUID, headers={'Connection':'close'}, auth=(context.configData["openSHR"]["username"], context.configData["openSHR"]["password"]))
        if (response.status_code > 204) :
            time.sleep(5)
            continue
        else :
            isSuccessful = True
            data = response.json()            
            # for now assert there are more than 2 obs record for te patient. we can test on display
            assert (len(data['results']) > 2)
            break
        response.close() 
        count += 1
    assert (isSuccessful)
      

def deleteOldOpenSHRRecords(context, deleteDataFileName): 
    logging.info ('Starting cleaning of previous run OpenSHR data')
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    # clean up old records
    try :
        delete_file = os.path.join(cur_dir, deleteDataFileName)        
        with open(delete_file) as deleteFile: 
            data = json.load(deleteFile)                 
    
        shrPatientUUIDs = data['shrPatientUUID']
        if (len(data['shrPatientUUID']) == 0) :
            return
            #delete shr patient record
        for shrPatientId in shrPatientUUIDs:                  
            deleteShrPerson(context, shrPatientId)
            logging.info ('Deleted OpenSHR Patient record for Id :' + shrPatientId)
    except :
        logging.error ('Encounted error when trying delete OpenSHR Person Record')
        assert (False)

def deleteShrPerson(context, shrPatientId): 
    count = 0     
    while (count < 5) :
        count += 1
        response = requests.delete(context.shrPatientUrl + str(shrPatientId), headers={'Content-Type': 'application/json', 'Connection':'close'}, auth=('admin', 'OpenSHR#123'))
        if (response.status_code > 204) :
            time.sleep(5)
            continue
        else :                   
            break
        response.close()      



