Feature: Post all Patient and Obs data into OpenMRS
		 

Scenario: Post Data to OpenMRS and validate that Case Reports are created for valid sentinel Events
When Patient and Observation data is posted to OpenMRS 
Then Case Report was created for each valid Sentinel Event
