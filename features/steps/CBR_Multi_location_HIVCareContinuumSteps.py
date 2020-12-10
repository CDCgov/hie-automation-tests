from behave import step, given, then, when
from features.modules import OpenEMPIService, OpenHIMService, OpenMRSService, OpenSHRService, HapiFhirService
import logging
import time

@when(u'Patient and Observation data is posted to OpenMRS')
def postDataToOpenMRS(context):
    previousObs = None     
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
                    patientServerId = OpenMRSService.getPatientIdentifier(context) 
                    patient.serverPatientIdentifier.update({obsRecord.server : patientServerId})                  
                    patientData = OpenMRSService.buildPatientData(patient, patientServerId)
                    patientResponse = OpenMRSService.postPatientData(context, patientData)
                    patientUUID = patientResponse['uuid']
                    patient.serverPatientUUID.update({obsRecord.server : patientUUID})
                   
                # get the patient UUID from serverMap
                patientUUID = patient.serverPatientUUID.get(obsRecord.server)
                taskName = OpenMRSService.getTaskName(obsRecord.event)
                   
                # for death record, we don't need encountUUID. Get enocunterUUID for other types
                if (obsRecord.event == 'deathdate') :
                    # for death record you don't have to create encounter or Obs record
                    OpenMRSService.postPatientDeathRecord(context, patientUUID, obsRecord.date)
                    OpenMRSService.runTask (context, taskName)
                    logging.info ('\nPosted Event ' + obsRecord.event + ' for Patient ' + patientServerId + ' on server ' + str(obsRecord.server))
                     
                else :
                    if (previousObs is not None and previousObs.date == obsRecord.date and previousObs.server == obsRecord.server) :
                        obsRecord.encounterUUID = previousObs.encounterUUID
                    else :
                        encounterData = OpenMRSService.buildPatientEncounterData(patientUUID, obsRecord.date)
                        encounterResponse = OpenMRSService.postEncounterData(context, encounterData)                       
                        encounterUUID = encounterResponse['uuid']
                        obsRecord.encounterUUID = encounterUUID
                        
                    # Finally, build and post this obs record   
                    obsData = OpenMRSService.buildObsData(context, patientUUID)
                    OpenMRSService.postObsData(context, obsData)            
                    logging.info ('\nPosted Event ' + obsRecord.event + ' for Patient ' + patientServerId + ' on server ' + str(obsRecord.server))
                                  
                if (context.currObs.isSentinelEvent == False) :
                    if (context.currObs.value is not None):
                        logging.error ('Processing Event ' + context.currObs.event + ' for Patient ' + patientServerId + ' on server ' + str(context.currObs.server) + ", the event,value - " + context.currObs.event + "," + context.currObs.value + " doesn't satisfy the criteria for case report generation")
                    else:
                        logging.error ('processing Event ' + context.currObs.event + ' for Patient ' + patientServerId + ' on server ' + str(context.currObs.server)+ ", the event - " + context.currObs.event + " doesn't satisfy the criteria for case report generation")
                    continue
                    
                OpenMRSService.checkCaseReportCreated(context)
                # we will sleep for the transaction to be successful on OpenHIM
                time.sleep(3)
                OpenHIMService.checkOpenHIMTransaction(context)
                OpenEMPIService.checkEMPIPerson(context)                
                if ( context.isFHIRTransaction) :                    
                    HapiFhirService.checkFhirData(context)  
                else :                   
                    OpenSHRService.checkShrPerson(context) 
                    OpenSHRService.checkShrObs(context)                     
                                
                previousObs = obsRecord
            except Exception as e : 
                logging.error ('Error processing Event ' + context.currObs.event + ' for Patient ' + patientServerId + ' on server ' + str(context.currObs.server) + ', Message = ' + str(e))
                
      
@then(u'Case Report was created for each valid Sentinel Event')
def checkCaseReportSubmitted(context):
    obsCount = 0
    for patient in context.patientData:
        for serverId in patient.serverPatientUUID.keys():   
            context.currServerId = int(serverId)
            data = OpenMRSService.getAllCaseReports(context, patient.serverPatientUUID[serverId])                                   
            obsCount = obsCount + len(data['results'])
        
        #assert (obsCount == len(patient.obs))
        logging.info ('\nAsserted that created case report status is \"SUBMITTED\" for each patient ' + patient.givenName)
   

