import requests
import logging
import urllib3
from features.model.Patient import Patient
from features.model.Obs import Obs
import random
import os
import json
from datetime import datetime, timedelta
import time


def __init__( context):          
    # Web service paths    
    context.DataFileName = context.configData["dataFileName"]   
    context.patientIdentifierPath = '/ws/rest/v1/idgen/nextIdentifier?source=1'
    context.patientPath = '/ws/rest/v1/patient'
    context.personPath = '/ws/rest/v1/person/'
    context.encounterPath = '/ws/rest/v1/encounter'
    context.obsPath = '/ws/rest/v1/obs'
    context.casereportPath = '/ws/rest/v1/casereport/casereport?personUUID='
    context.caseReportUUIDPath = '/ws/rest/v1/casereport/casereport/'
    context.taskPath = '/ws/rest/v1/taskaction'  
    #turns off storing EMPI Ids
    context.processedEMPI = True

# call this method to post 1 sentinel event record to OpenMRS    
def postDataBySentinelEventType(context, hivSentinelEventType):        
    foundRecord = False
    start_time = datetime.now()     
    # Identify the Obs record to post
    for patient in context.patientData:               
        for obsRecord in patient.obs:   
            # if no encounter data - means this obs record was not posted and can be posted
            if (obsRecord.event == hivSentinelEventType and obsRecord.encounterUUID == None):               
                # first get the server info, if server info doesn't exit, throw error
                context.currServerId = obsRecord.server                             
                # check if the patient is created in OpenMRS, if its not, create patient record
                if (obsRecord.server in patient.serverPatientIdentifier.keys()):
                    patientServerId = patient.serverPatientIdentifier.get(obsRecord.server)
                else :
                    patientServerId = getPatientIdentifier(context) 
                    patient.serverPatientIdentifier.update({obsRecord.server : patientServerId})                  
                    patientData = buildPatientData(patient, patientServerId)
                    patientResponse = postPatientData(context, patientData)
                    patientUUID = patientResponse['uuid']                   
                    patient.serverPatientUUID.update({obsRecord.server : patientUUID})
                
                foundRecord = True               
                context.currPatient = patient
                context.currObs = obsRecord
                break
        if (foundRecord):
            break
                
    if (not foundRecord):
        raise Exception ("No data is available of event of type " + hivSentinelEventType + ". Maybe all events were posted already.")
    
    # get the patient UUID from serverMap
    patientUUID = patient.serverPatientUUID.get(context.currServerId)
    if (obsRecord.event == 'deathdate') :
        # for death record you don't have to create encounter or Obs record
        postPatientDeathRecord(context, patientUUID, context.currObs.date) 
        end_time = datetime.now()
        logging.info ("\nPosted Sentinel Event data of type " + hivSentinelEventType.upper() + '(' + str((end_time - start_time).total_seconds()) + ')')
        return
                       
    # now that you have identified the Obs record to post,             
    # check if this Obs record belongs to an existing encounter, yes - use the encounter id, no - create encounter record
    for obsRecord in context.currPatient.obs:
        if (context.currObs.date == obsRecord.date and context.currObs.server == obsRecord.server and obsRecord.encounterUUID is not None):
            context.currObs.encounterUUID = obsRecord.encounterUUID    
            break
                    
    if (context.currObs.encounterUUID == None):
        encounterData = buildPatientEncounterData(patientUUID, context.currObs.date)
        encounterResponse = postEncounterData(context, encounterData)
        context.currObs.encounterUUID = encounterResponse['uuid']
                                
    # Finally, build and post this obs record   
    obsData = buildObsData(context, patientUUID)   
    postObsData(context, obsData)   
    end_time = datetime.now()
    logging.info ("\nPosted Sentinel Event data of type " + hivSentinelEventType.upper() + '(' + str((end_time - start_time).total_seconds()) + ')')

# Bulk load data from data file configured in config.json. 
def postAllData (context):
    previousObs = context.patientData[0].obs[0]
    previousObs.date = 0
    previousObs.server = 0  
    context.errors = []
    context.processedEMPI = False  
    # Identify the Obs record to post
    for patient in context.patientData:        
        context.currPatient = patient       
        for obsRecord in patient.obs: 
            try:
                context.currServerId = obsRecord.server
                context.currObs = obsRecord 
                # check if the patient is created in OpenMRS, if its not, create patient record
                if (obsRecord.server in patient.serverPatientIdentifier.keys()):
                    patientServerId = patient.serverPatientIdentifier.get(obsRecord.server)
                else :
                    patientServerId = getPatientIdentifier(context) 
                    patient.serverPatientIdentifier.update({obsRecord.server : patientServerId})                  
                    patientData = buildPatientData(patient, patientServerId)
                    patientResponse = postPatientData(context, patientData)
                    patientUUID = patientResponse['uuid']
                    patient.serverPatientUUID.update({obsRecord.server : patientUUID})
                  
                # get the patient UUID from serverMap
                patientUUID = patient.serverPatientUUID.get(obsRecord.server)                
                   
                # for death record, we don't need encountUUID. Get enocunterUUID for other types
                if (obsRecord.event == 'deathdate') :
                    # for death record you don't have to create encounter or Obs record
                    postPatientDeathRecord(context, patientUUID, obsRecord.date)                    
                    logging.info ('\nPosted Event ' + obsRecord.event + ' for Patient ' + patientServerId + ' on server ' + str(obsRecord.server))
                     
                else :
                    if (previousObs.date == obsRecord.date and previousObs.server == obsRecord.server) :
                        obsRecord.encounterUUID = previousObs.encounterUUID
                    else :
                        encounterData = buildPatientEncounterData(patientUUID, obsRecord.date)
                        encounterResponse = postEncounterData(context, encounterData)                       
                        encounterUUID = encounterResponse['uuid']
                        obsRecord.encounterUUID = encounterUUID
                        
                    # Finally, build and post this obs record   
                    obsData = buildObsData(context, patientUUID)
                    postObsData(context, obsData)            
                    logging.info ('Posted Event ' + obsRecord.event + ' for Patient ' + patientServerId + ' on server ' + str(obsRecord.server))
                
                previousObs = obsRecord
            except Exception as e : 
                context.errors.append(str(e))
                logging.error (str(e))
                      
def deleteOldOpenMRSRecords(context, deleteDataFileName): 
    logging.info ('Starting cleaning of previous run data')   
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    # clean up old records
    try :
        delete_file = os.path.join(cur_dir, deleteDataFileName)        
        with open(delete_file) as deleteFile: 
            data = json.load(deleteFile)                 
        openmrsUUID = data["openmrsPatientUUID"]    
        
        if (openmrsUUID != None) :
            #delete all case reports in all servers
            for serverId in openmrsUUID.keys():
                context.currServerId = int(serverId)
                personUUIDs = openmrsUUID.get(serverId)
                for personUUID in personUUIDs :                
                    data = getAllCaseReports(context, personUUID)               
                    for result in data['results']:       
                        deleteCaseReport(context, result['links'][0]['uri'])
                    logging.info ("Deleted all Case Report Records for Person - " + personUUID)                   
                    #delete person record
                    deletePerson(context, personUUID)
                   
    except :
        logging.error ('Encounted error when trying deleting OpenMRS Records')        

##-----------------------------Helper Methods-------------------------------------##

# load the data as a list of patients
def loadPatientData(context, dateFileName) :   
    # Read data file and load data
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    data_file = os.path.join(cur_dir, dateFileName)    
    with open(data_file) as dataFile:
        data=json.load(dataFile)    
     
    patients={}
    patientData = []
  
    #for quick retrieval of large datasets
    for patient in data["patients"]  :       
        patients.update({patient["identifier"]: Patient (patient ["identifier"], patient["givenName"], patient["middleName"], patient["familyName"], patient["gender"], patient["birthdate"])})


    for timeline in data["timelines"]:
        #get the patient obj
        patient = patients.get(timeline["identifier"])    
        #if patient is not in PatientData, then add it to the list
        if (patient not in patientData) :
            patientData.append(patient)        
        # add the current event 
        patient.obs.append(Obs (timeline.get("date"), timeline.get("event"), timeline.get("identifier"), timeline.get("value"), timeline.get("server")))
        
    #order the timelines after all data are loaded
    for patient in patientData:
        patient.obs.sort(key=lambda x: getattr(x, 'date'), reverse=True)
        count = 0
        for obs in patient.obs :
            if (count == 0 and obs.event == 'cd4Count') :                
                count += 1
                obs.isFirstCD4 = True
                
    patientData.sort(key=lambda x: x.identifier, reverse=False)    
    context.patientData = patientData


        
def getPatientIdentifier( context):    
    openMRSInstance = context.serverMap.get(context.currServerId)
    response = requests.get(openMRSInstance["baseUrl"] + context.patientIdentifierPath, auth=(openMRSInstance["username"], openMRSInstance["password"]))
    data = response.json()  
    response.close()
    return data['results'][0]["identifierValue"]

def buildPatientData( patientData, patientId):   
    data = {}
    person = {}
   
    person['birthdate'] =  (datetime.today() - timedelta(patientData.birthdate)).strftime('%Y-%m-%d')
    person['gender'] = patientData.gender
  
    names = {}  
    names['givenName'] = patientData.givenName
    names['middleName'] = patientData.middleName
    names['familyName'] = patientData.familyName
    person['names'] = [names]
    
    identifier = {}
    identifier['identifier'] = patientId
    identifier['identifierType'] = '05a29f94-c0ed-11e2-94be-8c13b969e334'
    data['person'] = person
    data['identifiers'] = [identifier]   
    return json.dumps(data)

def postPatientData( context, patientData):
    openMRSInstance = context.serverMap.get(context.currServerId)
    headers = {'Content-Type': 'application/json', 'Connection':'close'}  
    response = requests.post(openMRSInstance["baseUrl"] + context.patientPath, patientData, headers=headers, auth=(openMRSInstance["username"], openMRSInstance["password"]))
    data = response.json()
    response.close()
    return data

def deletePerson( context, patientUUID):    
    openMRSInstance = context.serverMap.get(context.currServerId)
    response = requests.delete(openMRSInstance["baseUrl"] + context.patientPath + "/" + patientUUID, headers={'Connection':'close'}, auth=('admin', 'Admin123'))
    response.close()
    logging.info ('Deleted Person record : ' + patientUUID)
   

def buildPatientEncounterData ( patientUUID, date):
    data = {}
    data['patient'] = patientUUID
    data['encounterType'] = 'd7151f82-c1f3-4152-a605-2f9ea7414a79'
    data['location'] = 'b1a8b05e-3542-4037-bbd3-998ee9c40574'
    data['encounterDatetime'] = (datetime.today() - timedelta(date)).strftime('%Y-%m-%d %H:%M:%S')      
    return json.dumps(data)  
 
    
def postEncounterData( context, encounterData):
    openMRSInstance = context.serverMap.get(context.currServerId)
    headers = {'Content-Type': 'application/json', 'Connection':'close'}   
    response = requests.post(openMRSInstance["baseUrl"] + context.encounterPath, encounterData, headers=headers, auth=(openMRSInstance["username"], openMRSInstance["password"]))
    data = response.json()
    response.close()
    return data
    

def buildObsData( context, personUUID) :    
    eventType = context.currObs.event
    eventDate = context.currObs.date
    value = context.currObs.value
    encounterUUID = context.currObs.encounterUUID
    
    obsDate = (datetime.today() - timedelta(days=eventDate, hours=random.randrange(11), minutes=random.randrange(30))).strftime('%Y-%m-%d %H:%M:%S')
    conceptUUID = getObsConceptUUID(eventType)   
    obsCodedValue = getObsCodedValue(conceptUUID, value) 
    
    context.currObs.isSentinelEvent = isSentinelEvent(context) 
     
    data = {}
    data['person']  = personUUID
    data['encounter'] = encounterUUID
    data['concept'] = conceptUUID
    data['value'] = obsCodedValue
    data['obsDatetime'] = obsDate
    
    return json.dumps(data)

def isSentinelEvent( context) :   
    if (context.currObs.event == 'hivTest' and context.currObs.value == 'negative') :
        return False
    elif (context.currObs.event == 'cd4Count' and (int(context.currObs.value) > 250 or context.currObs.isFirstCD4 == False)) :        
        return False 
    elif (context.currObs.event == 'viralLoad' and int(context.currObs.value) < 5000) :        
        return False
    elif (context.currObs.event == 'reasonArtStopped') :
        return False
    elif (context.currObs.event == 'weightChange') :
        return False   
    return True

def getObsConceptUUID( eventType):
    if (eventType == 'artStartDate') : 
        return '1255AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
    elif (eventType == 'cd4Count') :         
        return '5497AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
    elif (eventType == 'viralLoad') :
        return '856AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
    elif (eventType == 'reasonArtStopped') : 
        return '1252AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
    elif (eventType =='hivTest') :
        return '1040AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
    elif (eventType == 'reasonArtStopped') :
        return '1252AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
    elif (eventType == 'weightChange') :
        return '983AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
    else :
        logging.error ("Error: ConceptUUID is not found for eventType - " + eventType)

def getObsCodedValue( conceptUUID, value):
    codedValue = value
    if (conceptUUID == '1255AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA') :
        codedValue = '1256AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' 
    elif (conceptUUID == '1252AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA') :
        codedValue = '983AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
    elif (conceptUUID == '1040AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA') :
        if(value == 'positive'):
            codedValue = '703AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        elif(value == 'negative'):
            codedValue = '664AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
    return codedValue

def postObsData ( context, obsData):
    openMRSInstance = context.serverMap.get(context.currServerId)
    headers = {'Content-Type': 'application/json', 'Connection':'close'}  
    count = 0
    while (count < 5) :
        count += 1
        response = requests.post(openMRSInstance["baseUrl"] + context.obsPath, obsData, headers=headers, auth=(openMRSInstance["username"], openMRSInstance["password"]))    
        if (response.status_code > 204) :
            time.sleep(8)
            continue
        else :
            isSuccessful = True          
            break
        response.close()    
    data = response.json()

def postPatientDeathRecord( context, personUUID, date):
    data = {}
    data ['uuid'] = personUUID
    data['causeOfDeath'] = '125574AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
    data['dead'] = 'true'
    data['deathDate'] = (datetime.today() - timedelta(days=date, hours=2)).strftime('%Y-%m-%d %H:%M:%S')     
    request = json.dumps(data)
    
    openMRSInstance = context.serverMap.get(context.currServerId)
    headers = {'Content-Type': 'application/json', 'Connection':'close'}   
    response = requests.post(openMRSInstance["baseUrl"] + context.personPath + personUUID, request, headers=headers, auth=(openMRSInstance["username"], openMRSInstance["password"]))
    responseData = response.json()  
    response.close()
    return responseData

#-------------------Scheduler task methods---------------------    
    
def getTaskData( taskName): 
    data = {}
    data["action"] = "runtask"
    tasks = [taskName]   
    data["tasks"] = tasks
    return json.dumps(data)

def runTask( context, taskName):    
    openMRSInstance = context.serverMap.get(context.currServerId)
    headers = {'Content-Type': 'application/json', 'Connection':'close'} 
    data =  getTaskData(taskName) 
    response = requests.post(openMRSInstance["baseUrl"] + context.taskPath, data, headers=headers, auth=(openMRSInstance["username"], openMRSInstance["password"]))
    data = response.json()
    response.close()
    return data

def getTaskName( eventType):
    if (eventType == 'hivTest') :
        return 'New HIV Case'
    elif (eventType == 'artStartDate') :
        return 'New HIV Treatment'
    elif (eventType == 'cd4Count') :
        return 'HIV First CD4 Count'
    elif (eventType == 'viralLoad') :
        return 'HIV Treatment Failure'
    elif (eventType == 'deathdate') :
        return 'HIV Patient Died'    
    logging.error ("The event type - " + eventType +" is not configured in the module. Set it up like the other Event types (hivTest,artStartDate)")

#----------------Case Report Methods---------------------------------

def checkCaseReportCreated( context):   
    #If the Obs data posted does not satisfy trigger condition, then no case report will be created
    if (context.currObs.isSentinelEvent == False) :         
        obsRecord = context.currObs       
        patientServerId = context.currPatient.serverPatientIdentifier.get(obsRecord.server)
        logging.info ('No case report will be created for Patient ' + patientServerId + ' on server ' + str(obsRecord.server) + ", for event-value :: " + obsRecord.event + "-" + obsRecord.value)
        return
    
    taskName = getTaskName(context.currObs.event)       
    runTask(context, taskName)     
    
    patientUUID = context.currPatient.serverPatientUUID.get(context.currServerId)    
    crData = getCaseReport(context, patientUUID) 
    
    if (taskName not in crData['display']) :
        # check if this is valid, 
        taskName = 'HIV Treatment Failure'
        runTask(context, taskName) 
        patientUUID = context.currPatient.serverPatientUUID.get(context.currServerId)
        crData = getCaseReport(context, patientUUID)
    logging.info("Requested CBR Scheduler Task " + taskName + " to execute")
    assert (taskName in crData['display'])
    context.currTaskName = taskName
    

def checkCaseReportStatus(context):   
    if (context.currObs.isSentinelEvent == False) :     
        return    
    patientUUID = context.currPatient.serverPatientUUID.get(context.currServerId)
    crData = getCaseReport(context, patientUUID) 
    
    if (context.currTaskName in crData['display']) :        
        data = getCaseReportRecord (context, crData['links'][0]['uri'])           
        if (data['status'] != 'SUBMITTED'):
            logging.info ("*Case report " + data['uuid'] + " was not submitted successfully")
            #assert (False)
            
        else:
            logging.info ("*Case report " + data['uuid'] + " was submitted successfully")
        return True   
    else :
        return True 

def getCaseReport(context, personUUID):
    openMRSInstance = context.serverMap.get(context.currServerId) 
    response = None 
    count = 0
    while (count < 5) :
        count += 1
        response = requests.get(openMRSInstance["baseUrl"] + context.casereportPath + personUUID, headers={'Connection':'close'}, auth=(openMRSInstance["username"], openMRSInstance["password"]))    
        if (response.status_code > 204) :
            time.sleep(5)
            continue
        else :                    
            break
              
    data = response.json()      
    return data['results'][-1]

def getAllCaseReports(context, personUUID):    
    openMRSInstance = context.serverMap.get(context.currServerId)   
    response = requests.get(openMRSInstance["baseUrl"] + context.casereportPath + personUUID, headers={'Connection':'close'},  auth=(openMRSInstance["username"], openMRSInstance["password"]))    
    data = response.json()
    response.close()
    return data

def deleteCaseReport (context, url):    
    openMRSInstance = context.serverMap.get(context.currServerId)   
    response = requests.delete(url, headers={'Connection':'close'}, auth=(openMRSInstance["username"], openMRSInstance["password"]))   
    response.close()    

def getCaseReportRecord(context, url):
    openMRSInstance = context.serverMap.get(context.currServerId)    
    response = None 
    count = 0
    while (count < 5) :
        count += 1
        response = requests.get(url, auth=(openMRSInstance["username"], openMRSInstance["password"]))    
        if (response.status_code > 204) :
            time.sleep(5)
            continue
        else :                     
            break
        response.close()    
      
    data = response.json()  
    return data   
