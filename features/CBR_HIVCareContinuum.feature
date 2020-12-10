Feature: Post HIV sentinal events for Ms. Smith's continuum of care. Automate the testing of Case Report Flow


Scenario:HIV Diagnosis
When a positive HIV diagnosis for Ms. Smith is posted to OpenMRS
Then A Case Report is created for positive HIV diagnosis of Ms. Smith
And the created CaseReport is sent to OpenHIM
And OpenHIM gets a Global Patient Identifier for the patient from OpenEMPI
And CaseReport with global identifier is sent to Centralized Repository from OpenHIM
And CaseReport status in OpenMRS is updated as Submitted

Scenario:ART initiation
When ART is initiated for Ms.Smith
Then A Case Report is created for ART is initiation of Ms. Smith
And the created CaseReport is sent to OpenHIM
And OpenHIM gets a Global Patient Identifier for the patient from OpenEMPI
And CaseReport with global identifier is sent to Centralized Repository from OpenHIM
And CaseReport status in OpenMRS is updated as Submitted

Scenario:First CD4 count
When a cd4 test is available for Ms.Smith
Then A Case Report is created with cd4 information of Ms. Smith
And the created CaseReport is sent to OpenHIM
And OpenHIM gets a Global Patient Identifier for the patient from OpenEMPI
And CaseReport with global identifier is sent to Centralized Repository from OpenHIM
And CaseReport status in OpenMRS is updated as Submitted

Scenario:Viral Load
When a viral load test is available for Ms.Smith
Then A Case Report is created with viral load information for Ms. Smith
And the created CaseReport is sent to OpenHIM
And OpenHIM gets a Global Patient Identifier for the patient from OpenEMPI
And CaseReport with global identifier is sent to Centralized Repository from OpenHIM
And CaseReport status in OpenMRS is updated as Submitted

Scenario:Death
When Ms. Smith dies
Then A Case Report Module is created that shows Ms. Smith has died
And the created CaseReport is sent to OpenHIM
And OpenHIM gets a Global Patient Identifier for the patient from OpenEMPI
And CaseReport with global identifier is sent to Centralized Repository from OpenHIM
And CaseReport status in OpenMRS is updated as Submitted