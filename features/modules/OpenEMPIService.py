import logging
import time
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import json

#initialize
def __init__(context):
    context.empiPersonUrl = context.configData["openEMPI"]["baseUrl"] + '/person-query-resource/findPersonById'
    context.empiAuthenticationUrl = context.configData["openEMPI"]["baseUrl"] + '/security-resource/authenticate'
    context.empiDeletePersonUrl = context.configData["openEMPI"]["baseUrl"] + '/person-manager-resource/deletePerson'   

       
def checkEMPIPerson(context):
    if (context.currObs.isSentinelEvent == False) :     
        return  
    context.processedEMPI = True    
    start_time = datetime.now() 
    patientId = context.currPatient.serverPatientIdentifier.get(context.currServerId)     
    response = getEMPIPerson(context, patientId)
        
    try :    
        root = ET.fromstring(response.content)   
        identifier = root.iter('personIdentifiers')
   
        # assert that the persons identifier contains the global identifier for the openmrs person id
        personIdentifiers = list(identifier)           
        if (personIdentifiers[0].find('identifier').text.strip == patientId.strip):                    
            assert (len(personIdentifiers[1].find('identifier').text) > 7)
        elif (personIdentifiers[1].find('identifier').text == patientId):
            assert (len(personIdentifiers[0].find('identifier').text) > 7)
        end_time = datetime.now()
        logging.info("Confirm EMPI has a Global Id for Patient (" + str((end_time - start_time).total_seconds()) + ')')
        
    except :
        logging.error ('Encounted when trying to check EMPI data. This transaction would have been rolled back and the user needs to submit the report manually' )
        assert (False)

def getEMPIPerson(context, patientId):  
    nheaders = {'Content-Type': 'application/xml', 'Connection':'close'}  
    response = requests.put(context.empiAuthenticationUrl , buildEmpiAuthenticateRequest(context), headers=nheaders)  
    sessionKey = response.text
    
    pheaders = {'Content-Type': 'application/xml', 'Connection':'close', 'OPENEMPI_SESSION_KEY': sessionKey}
    response = None
    count = 0
    while count < 5 :
        count += 1
        try :
            response = requests.post(context.empiPersonUrl, buildEmpiPersonRequest(context, patientId), headers=pheaders)
            if (response.status_code == 200) :                
                break
        except :
            time.sleep(10)
    return response

def deleteEMPIPerson(context, personId):  
    nheaders = {'Content-Type': 'application/xml', 'Connection':'close'}  
    response = requests.put(context.empiAuthenticationUrl , buildEmpiAuthenticateRequest(context), headers=nheaders)  
    sessionKey = response.text
    response.close()

    pheaders = {'Content-Type': 'application/xml', 'Connection':'close', 'OPENEMPI_SESSION_KEY': sessionKey}
    response = requests.put(context.empiDeletePersonUrl, buildEmpiPersonRequest(context, personId), headers=pheaders)
    logging.info ("Deleted EMPI Person Record, Identifier : " + personId)  
    response.close()
    
def buildEmpiAuthenticateRequest(context):
    return "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><authenticationRequest><password>" + context.configData["openEMPI"]["password"] + "</password><username>" + context.configData["openEMPI"]["username"] + "</username></authenticationRequest>"

def buildEmpiPersonRequest(context, patientIdentifier):   
    openMRSInstance = context.serverMap.get(context.currServerId)   
    return '<personIdentifier><identifier>' + patientIdentifier  + '</identifier><identifierDomain><identifierDomainName>' + openMRSInstance["instanceName"] + '</identifierDomainName></identifierDomain></personIdentifier>'
                        
def deleteOldEMPIRecords(context, deleteDataFileName): 
    logging.info ('Starting cleaning of previous run EMPI data')
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    # clean up old records
    try :
        delete_file = os.path.join(cur_dir, deleteDataFileName)        
        with open(delete_file) as deleteFile:                 
            data = json.load(deleteFile) 
        
        openmrsPatientIds = data["empiGlobalIds"]            
        if (len(openmrsPatientIds) > 0) :
            #delete all case reports in all servers        
            for serverId in openmrsPatientIds.keys():            
                context.currServerId = int(serverId)           
                personIdentifiers = openmrsPatientIds.get(serverId)            
                for personIdentifier in personIdentifiers :                          
                    deleteEMPIPerson(context, personIdentifier)
    except Exception as e: 
        logging.error ("Delete error - " + str(e))

            
                        