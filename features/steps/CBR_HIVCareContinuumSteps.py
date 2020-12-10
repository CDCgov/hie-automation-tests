from behave import step, given, then, when
from features.modules import OpenEMPIService, OpenHIMService, OpenMRSService, OpenSHRService, HapiFhirService

@when(u'a positive HIV diagnosis for Ms. Smith is posted to OpenMRS')
def step_impl(context):    
    OpenMRSService.postDataBySentinelEventType(context, 'hivTest')

@then(u'A Case Report is created for positive HIV diagnosis of Ms. Smith')
def step_impl(context):
    OpenMRSService.checkCaseReportCreated(context)

@then(u'the created CaseReport is sent to OpenHIM')
def step_impl(context):
    OpenHIMService.checkOpenHIMTransaction(context)

@then(u'OpenHIM gets a Global Patient Identifier for the patient from OpenEMPI')
def step_impl(context):
    OpenEMPIService.checkEMPIPerson(context)

@then(u'OpenHIM sends the CaseReport with global identifier to OpenSHR')
def step_impl(context):
    OpenSHRService.checkShrPerson(context)

@then(u'the CaseReport is saved in OpenSHR')
def step_impl(context):
    OpenSHRService.checkShrObs(context)

@then(u'CaseReport status in OpenMRS is updated as Submitted')
def step_impl(context):
    OpenMRSService.checkCaseReportStatus(context)

@when(u'ART is initiated for Ms.Smith')
def step_impl(context):
    OpenMRSService.postDataBySentinelEventType(context, 'artStartDate')

@then(u'A Case Report is created for ART is initiation of Ms. Smith')
def step_impl(context):
    OpenMRSService.checkCaseReportCreated(context)

@when(u'a cd4 test is available for Ms.Smith')
def step_impl(context):
    OpenMRSService.postDataBySentinelEventType(context, 'cd4Count')

@then(u'A Case Report is created with cd4 information of Ms. Smith')
def step_impl(context):
    OpenMRSService.checkCaseReportCreated(context)

@when(u'a viral load test is available for Ms.Smith')
def step_impl(context):
    OpenMRSService.postDataBySentinelEventType(context, 'viralLoad')

@then(u'A Case Report is created with viral load information for Ms. Smith')
def step_impl(context):
    OpenMRSService.checkCaseReportCreated(context)

@when(u'Ms. Smith dies')
def step_impl(context):
    OpenMRSService.postDataBySentinelEventType(context, 'deathdate')

@then(u'A Case Report Module is created that shows Ms. Smith has died')
def step_impl(context):
    OpenMRSService.checkCaseReportCreated(context)

@then(u'CaseReport with global identifier is sent to Centralized Repository from OpenHIM')
def step_impl(context):
    if (context.isFHIRTransaction) :
        HapiFhirService.checkFhirData(context)
    else :
        #will be tested as part of next step
        OpenSHRService.checkShrPerson(context)
