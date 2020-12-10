from features.modules import OpenMRSService, OpenHIMService, OpenEMPIService, OpenSHRService, HapiFhirService
import json
import os
import logging
import urllib3

def initialize(context):  
    OpenMRSService.__init__(context) 
    OpenHIMService.__init__(context)   
    OpenEMPIService.__init__(context)  
    OpenSHRService.__init__(context)
    HapiFhirService.__init__(context)
    
def loadPatientData(context):   
    OpenMRSService.loadPatientData(context, "../data/" + context.DataFileName)     

def cleanPreviousRunData(context):
    #CLEAN previous RUN DATA   
    deleteFileName = '../data/delete.json'
    OpenMRSService.deleteOldOpenMRSRecords(context, deleteFileName)
    OpenHIMService.deleteOldOpenHIMTransactions(context)
    OpenEMPIService.deleteOldEMPIRecords(context, deleteFileName)
    OpenSHRService.deleteOldOpenSHRRecords(context, deleteFileName)
    HapiFhirService.deleteOldHapiFhirRecords(context, deleteFileName)
    logging.info ("Done cleaning previous Run Data")
    
def loadConfigData(context):
    #logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w', format='%(message)s')    
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    cur_dir = os.path.abspath(os.path.dirname(__file__))    
   
    config_file = os.path.join(cur_dir, "../config/config.json")
    with open(config_file) as configFile:
        config=json.load(configFile)        
    
    context.configData = config  
    
    # Load the server info into server map for quick retrieval 
    context.serverMap = {}    
    for openMRSInstance in context.configData ["openmrsInstances"] :
        context.serverMap.update({openMRSInstance['id'] : openMRSInstance})

    logging.info ('Loaded Configuration data') 

    
def storeRunData(context):    
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    deleteFile = os.path.join(cur_dir, "../data/delete.json")            

    data = {}
    serverPatientUUIDDict = {}
    shrPatientUUIDs = []
    hapiFhirUUIDs = []
    
    for patient in context.patientData:
        for serverId in patient.serverPatientUUID.keys():            
            patientUUID = patient.serverPatientUUID.get(serverId)            
            if (serverId not in serverPatientUUIDDict.keys()):                
                serverPatientUUIDDict.update({serverId : []})
            serverPatientUUIDDict.get(serverId).append(patientUUID)
        
        if (patient.shrPatientUUID != None) :
            shrPatientUUIDs.append (patient.shrPatientUUID)
            
        if (patient.fhirPatientUUID != None) :           
            hapiFhirUUIDs.append (patient.fhirPatientUUID)
        
    serverPatientIdentifierDict = {}
    for patient in context.patientData:        
        for serverId in patient.serverPatientIdentifier.keys():            
            patientId = patient.serverPatientIdentifier.get(serverId)            
            if (serverId not in serverPatientIdentifierDict.keys()):                
                serverPatientIdentifierDict.update({serverId : []})
            serverPatientIdentifierDict.get(serverId).append(patientId)
        
    data['openmrsPatientUUID'] = serverPatientUUIDDict
    data['shrPatientUUID'] = shrPatientUUIDs
    data['hapiFhirPatientUUID'] = hapiFhirUUIDs
    # fix for test OpenMRS
    if (context.processedEMPI or context.processedEMPI is None) :        
        data['empiGlobalIds'] = serverPatientIdentifierDict
    
    with open(deleteFile, 'w') as outfile:        
        json.dump(data, outfile)
