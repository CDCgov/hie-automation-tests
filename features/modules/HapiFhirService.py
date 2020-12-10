import logging
import time
import requests
import os
import json

#constructor
def __init__(context):       
    context.fhirPatientLkUrl = context.configData["HAPI-FHIR"]["baseUrl"] + '/Patient?'
    context.fhirObservationLkUrl = context.configData["HAPI-FHIR"]["baseUrl"] + '/Observation?'
    context.fhirPatientUrl = context.configData["HAPI-FHIR"]["baseUrl"] + '/Patient/'
    context.fhirEncounterUrl =  context.configData["HAPI-FHIR"]["baseUrl"] + '/Encounter?patient='
    context.fhirObservationUrl =  context.configData["HAPI-FHIR"]["baseUrl"] + '/Observation?patient='
    
def deleteOldHapiFhirRecords(context, deleteDataFileName): 
    logging.info ('Starting cleaning of previous run HAPI-FHIR data')
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    # clean up old records
    try :
        
        delete_file = os.path.join(cur_dir, deleteDataFileName)        
        with open(delete_file) as deleteFile: 
            data = json.load(deleteFile)                 
                    
        if (len(data['hapiFhirPatientUUID']) == 0) :
            return              
        #delete shr patient record
        
        for hapiFhirPatientId in data['hapiFhirPatientUUID']:   
            deleteFhirPatient(context, hapiFhirPatientId)           
           
    except :
        logging.error ('Encounted error when trying delete Hapi Fhir Person Record')
        
                   
def deleteFhirPatient(context, hapiFhirPatientId):  
    # HAVE to redo this later
    response = requests.get(context.fhirPatientUrl + hapiFhirPatientId, headers={'Connection':'close'})  
    data = response.json()
    familyName = data['name'][0]['family']
    given = data['name'][0]['given'][0]
    
    lkInfo = 'family=' + familyName + "&given=" + given        
    response = requests.get(context.fhirPatientLkUrl + lkInfo, headers={'Connection':'close'})
    data = response.json()
    for entry in data['entry'] :
        resourceID = entry['resource']['id']      
        deleteFhirEncounter (context, resourceID)
        deleteFhirObservation (context, resourceID)
        response = requests.delete(entry['fullUrl'], headers={'Connection':'close'})        
        response.close()
    logging.info("Deleted hapi-fhir person, Encounter, Observation records for " + familyName + "," + given)
        
def deleteFhirEncounter(context, hapiFhirPatientId):      
    response = requests.delete(context.fhirEncounterUrl + hapiFhirPatientId, headers={'Connection':'close'})  
    data = response.json() 
    response.close()    
        
def deleteFhirObservation(context, hapiFhirPatientId):          
    response = requests.delete(context.fhirObservationUrl + hapiFhirPatientId, headers={'Connection':'close'})  
    data = response.json() 
    response.close()    

def checkFhirData(context) :    
    #check person data exists
    logging.info("Check HAPI-FHIR for Patient - " + context.currPatient.givenName)
    count = 0 
    isSuccessful = False
    while (count < 5 and isSuccessful == False) :          
        lkInfo = 'family=' + context.currPatient.familyName + "&given=" + context.currPatient.givenName        
        response = requests.get(context.fhirPatientLkUrl + lkInfo, headers={'Connection':'close'})
        count += 1
        if (response.status_code > 204) :
            time.sleep(5)
            continue
        else :
            isSuccessful = True
            data = response.json() 
            context.currPatient.fhirPatientUUID = data['entry'][0]['resource']['id']           
            break
        
    response.close()         
    assert (isSuccessful)
