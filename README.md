# HIE Automation Testing Framework     
HIE Automation Testing framework was built using Python and Behave to support automation testing of different HIE systems. Currently, this project automates the testing of the OpenMRS data load and  Case Based Reporting Module (CBR) workflows. Data is posted to OpenMRS and the state of the data is tested in different HIE systems (OpenMRS, OpenHIM, OpenSHR, OpenEMPI, and HAPI-FHIR)     

# Getting Started    
Currently, the testing framework contains 3 automation tests, one tests the bulk data load to OpenMRS and other 2 tests OpenMRS Case based Reporting module’s workflows.  
  
## Testing data load into OpenMRS  
OpenMRS_BulkHIVDataLoad, A simple test that tests the bulk data load into an instance of OpenMRS and provides the user with the stats (Number of patients, encounters and observations records loaded).  
  
### Assumptions    
User is familiarity with OpenMRS, Python, and BDD framework Behave is assumed.  Familiarity with HIE components is recommended.  
  
### Prerequisites     
OpenMRS_BulkHIVDataLoad needs the following software -   
  	Python version >= 3.7     
  	Behave version >= 1.2    
  	OpenMRS Platform version >= 2.2   
  
### Configuration  
Update the config.json located under the config folder. Only 2 config elements (“datafilename” and “openmrsInstances”) are needed for this test. The other elements in the config file can be there or can be removed. They are optional. The value of datafilename needs to be “simulatordataset-large.json” and openmrsInstances needs to be configured with at least one OpenMRS instance information.  
-	id    	        :   A unique value,  gets tied to the “server” value in the dataset files located under data folder. If you add or modify this value, make                     	  	  	           sure the datasets are also updated.  
-	instanceName    :   Can be any name, it’s for tester’s clarity.  
-	baseUrl   	    :   Replace server and port with OpenMRS instance info  
-	username        :   Username that can access the services of the above instance  
-	password        :   Password of the above user  
  
### Executing the test  
You can execute the test with the below statement.  
     	behave --no-logcapture --include ./features/OpenMRS_BulkHIVDataLoad   
  
#### Test Result : After the test executes, the user will see the stats being printed on the console.  
Additionally, the user can query the Patient, Encounter and Obs tables to see the data posted.  
  
## Testing CBR with OpenMRS, OpenHIM, OpenEMPI and HAPI-FHIR  
Two tests (CBR_HIVCareContinuum and  CBR_Multi_location_HIVCareContinuumSteps) were developed to test CBR (Case Based Reporting) workflow that uses HAPI-FHIR as shared health record as repository.  
   
### Assumptions    
User is familiarity with OpenMRS, OpenMRS Case Based Reporting (CBR) Module, Python, and BDD framework Behave is assumed.  Familiarity with HIE components is recommended.  
  
### Prerequisites      
Both CBR_HIVCareContinuum and CBR_Multi_location_HIVCareContinuum tests needs the following software   
  
  	Python version >= 3.7     
  	Behave version >= 1.2    
  	OpenMRS Platform version >= 2.2    
  	OpenMRS Module - Case Based Module version >= 2.0  (Not yet released)  
  	OpenMRS Module IDGen version >= 4.7    
    OpenEMPI platform >= 3.5.0c  
    OpenHIM platform >= 1.13   
  	OpenHIM FHIR-Mediator >= Latest (Not yet released)   HAPIFHIR instance >= 4.2.0 
    
Note: CBR module must be configured (OpenMRS Home -> Case Reports ->Configure) to use Case Report Format as HL7 FHIR  	  	  
  
### Configuration  
Update the config.json located under the config folder. All elements except OpenSHR is required for this test.   
-	openmrsInstances needs to be configured with at least one OpenMRS instance.  
-	id       	    :   A unique value,  gets tied to the “server” value in the dataset files located under data folder. If you add or modify this value,  make sure the datasets are also updated.  
-	instanceName    : Can be any name, it’s for tester’s clarity.  
-	baseUrl   	     : Replace server and port with OpenMRS instance info  
-	username   : Username that can access the services of the above instance  
-	password   : Password of the above user  
-	openHIM : configuration details for OpenHIM core   
-	baseUrl  	 : replace server and port with OpenHIM core instance info  
-	username   : username that can access the above instance  
-	password    : password of the above user  
-	openEMPI : configuration details for OpenEMPI rest services  
-	baseUrl   	: replace server and port with OpenEMPI rest services info  
-	username  : username that can access the rest services  
-	password  : password of the above user  
-	HAPI-FHIR : configuration details of hapi-fhir instance  
-	baseUrl  	: replace server and port with hapi-fhir instance  
-	username  : username that can access the services of the above instance  
-	password  : password of the above user  
  
###  Executing the test  

#### CBR_HIVCareContinuum  
This test tests the entire workflow of Case Based Reporting module. Based on the order of the events (Obs) specified on the Gherkin file, events (Obs) are posted to OpenMRS. For each event posted, the test confirms that -   
1.	A Case report is created in OpenMRS  
2.	Transaction is sent OpenHIM  
3.	Patient Record is created or exists in OpenEMPI  
4.	The case report gets stored in HAPI-FHIR   
  
##### Additional Configuration : Before you execute this test, please update config.json, set dataFilename value as simulator-dataset-small.json  
 You can execute the test with the below statement.  
   	behave --no-logcapture --include ./features/CBR_HIVCareContinuum  
  
#### CBR_Multi_location_HIVCareContinuum  
This test also tests the entire workflow of Case Based Reporting module. But instead of posting data based on event as the previous test CBR_HIVCareContinuumSteps does, this test reads the data file, posts Patient records into multiple OpenMRS instances and posts all sentinel events sorted by date to OpenMRS instances. For each posted sentinel event, the test confirms that   
1. A Case report is created in the OpenMRS instance the event was posted to. 2. Transaction is sent OpenHIM  
3.	Patient Record is created or exists in OpenEMPI  
4.	The case report gets stored in HAPI-FHIR or OpenSHR (based on the configuration in CBR module)  
  
##### Additional Configuration: Before you execute this test, please update config.json, set dataFilename value as simulator-dataset-multiple-instances.json. Also, you need at least 2 OpenMRS instances running for this test.  
  
 You can execute the test with the below statement.  
   	behave --no-logcapture --include ./features/CBR_Multi_location_HIVCareContinuum  
  
Testing CBR with OpenMRS, OpenHIM, OpenEMPI and OpenHSR  
Two tests (CBR_HIVCareContinuum and  CBR_Multi_location_HIVCareContinuumSteps) discussed can also be used to CBR (Case Based Reporting) workflow that uses OpenSHR as shared health repository .  
   
Assumptions    
User is familiarity with OpenMRS, OpenMRS Case Based Reporting (CBR) Module, Python, and BDD framework Behave is assumed.  Familiarity with HIE components is recommended.  
  
Prerequisites     
CBR_HIVCareContinuum and CBR_Multi_location_HIVCareContinuumSteps needs the following software   
  
  	Python version >= 3.7     
  	Behave version >= 1.2    
  	OpenMRS Platform version >= 2.2    
  	OpenMRS Module - Case Based Module version >= 2.0  (Not yet released)  
  	OpenMRS Module IDGen version >= 4.7    
          OpenEMPI platform >= 3.5.0c            OpenHIM platform >= 1.13   
  	OpenHIM XDS-Mediator >= Latest (https://github.com/jembi/openhim-mediator-xds)  
  	OpenMRS instance with OpenSHR >= Latest (https://github.com/jembi/openshr)  
  
Note: CBR module must be configured (OpenMRS Home -> Case Reports ->Configure) to use Case Report Format as HL7 CDA  	  
  
Configuration  
Update the config.json located under the config folder. All elements except HAPI-FHIR is needed for this test.   
-	openmrsInstances needs to be configured with at least one OpenMRS instance.  
-	id       	    :   A unique value,  gets tied to the “server” value in the dataset     	  	  	       files located under data folder. If you add or modify this    	  	  	  	       value,  make sure the datasets are also updated.  
-	instanceName    : Can be any name, it’s for tester’s clarity.  
-	baseUrl   	     : Replace server and port with OpenMRS instance info  
-	username   : Username that can access the services of the above instance  
-	password   : Password of the above user  
-	openHIM : configuration details for OpenHIM core   
-	baseUrl  	 : replace server and port with OpenHIM core instance info  
-	username   : username that can access the above instance  
-	password    : password of the above user  
-	openEMPI : configuration details for OpenEMPI rest services  
-	baseUrl   	: replace server and port with OpenEMPI rest services info  
-	username  : username that can access the rest services  
-	password  : password of the above user  
-	openSHR : configuration details for OpenSHR instance  
-	baseUrl   	: replace server and port with OpenSHR instance  
-	username  : username that can access the services  
-	password  : password of the above user  
  
  	  
Executing the test  
CBR_HIVCareContinuum  
Additional Configuration : Before you execute this test, please update config.json, set dataFilename value as simulator-dataset-small.json  
 You can execute the test with the below statement.  
   	behave --no-logcapture --include ./features/CBR_HIVCareContinuum  
  
CBR_Multi_location_HIVCareContinuum  
Additional Configuration: Before you execute this test, please update config.json, set dataFilename value as simulator-dataset-multiple-instances.json. Also, you need at least 2 OpenMRS instances running for this test.  
  
 You can execute the test with the below statement.  
   	behave --no-logcapture --include ./features/CBR_Multi_location_HIVCareContinuum  


# CDCgov GitHub Organization Open Source Project Template

**Template for clearance: This project serves as a template to aid projects in starting up and moving through clearance procedures. To start, create a new repository and implement the required [open practices](open_practices.md), train on and agree to adhere to the organization's [rules of behavior](rules_of_behavior.md), and [send a request through the create repo form](https://forms.office.com/Pages/ResponsePage.aspx?id=aQjnnNtg_USr6NJ2cHf8j44WSiOI6uNOvdWse4I-C2NUNk43NzMwODJTRzA4NFpCUk1RRU83RTFNVi4u) using language from this template as a Guide.**

**General disclaimer** This repository was created for use by CDC programs to collaborate on public health related projects in support of the [CDC mission](https://www.cdc.gov/about/organization/mission.htm).  GitHub is not hosted by the CDC, but is a third party website used by CDC and its partners to share information and collaborate on software. CDC use of GitHub does not imply an endorsement of any one particular service, product, or enterprise. 

## Access Request, Repo Creation Request

* [CDC GitHub Open Project Request Form](https://forms.office.com/Pages/ResponsePage.aspx?id=aQjnnNtg_USr6NJ2cHf8j44WSiOI6uNOvdWse4I-C2NUNk43NzMwODJTRzA4NFpCUk1RRU83RTFNVi4u) _[Requires a CDC Office365 login, if you do not have a CDC Office365 please ask a friend who does to submit the request on your behalf. If you're looking for access to the CDCEnt private organization, please use the [GitHub Enterprise Cloud Access Request form](https://forms.office.com/Pages/ResponsePage.aspx?id=aQjnnNtg_USr6NJ2cHf8j44WSiOI6uNOvdWse4I-C2NUQjVJVDlKS1c0SlhQSUxLNVBaOEZCNUczVS4u).]_

## Related documents

* [Open Practices](open_practices.md)
* [Rules of Behavior](rules_of_behavior.md)
* [Thanks and Acknowledgements](thanks.md)
* [Disclaimer](DISCLAIMER.md)
* [Contribution Notice](CONTRIBUTING.md)
* [Code of Conduct](code-of-conduct.md)

## Overview

Describe the purpose of your project. Add additional sections as necessary to help collaborators and potential collaborators understand and use your project.
  
## Public Domain Standard Notice
This repository constitutes a work of the United States Government and is not
subject to domestic copyright protection under 17 USC § 105. This repository is in
the public domain within the United States, and copyright and related rights in
the work worldwide are waived through the [CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/).
All contributions to this repository will be released under the CC0 dedication. By
submitting a pull request you are agreeing to comply with this waiver of
copyright interest.

## License Standard Notice
The repository utilizes code licensed under the terms of the Apache Software
License and therefore is licensed under ASL v2 or later.

This source code in this repository is free: you can redistribute it and/or modify it under
the terms of the Apache Software License version 2, or (at your option) any
later version.

This source code in this repository is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the Apache Software License for more details.

You should have received a copy of the Apache Software License along with this
program. If not, see http://www.apache.org/licenses/LICENSE-2.0.html

The source code forked from other open source projects will inherit its license.

## Privacy Standard Notice
This repository contains only non-sensitive, publicly available data and
information. All material and community participation is covered by the
[Disclaimer](https://github.com/CDCgov/template/blob/master/DISCLAIMER.md)
and [Code of Conduct](https://github.com/CDCgov/template/blob/master/code-of-conduct.md).
For more information about CDC's privacy policy, please visit [http://www.cdc.gov/other/privacy.html](https://www.cdc.gov/other/privacy.html).

## Contributing Standard Notice
Anyone is encouraged to contribute to the repository by [forking](https://help.github.com/articles/fork-a-repo)
and submitting a pull request. (If you are new to GitHub, you might start with a
[basic tutorial](https://help.github.com/articles/set-up-git).) By contributing
to this project, you grant a world-wide, royalty-free, perpetual, irrevocable,
non-exclusive, transferable license to all users under the terms of the
[Apache Software License v2](http://www.apache.org/licenses/LICENSE-2.0.html) or
later.

All comments, messages, pull requests, and other submissions received through
CDC including this GitHub page may be subject to applicable federal law, including but not limited to the Federal Records Act, and may be archived. Learn more at [http://www.cdc.gov/other/privacy.html](http://www.cdc.gov/other/privacy.html).

## Records Management Standard Notice
This repository is not a source of government records, but is a copy to increase
collaboration and collaborative potential. All government records will be
published through the [CDC web site](http://www.cdc.gov).

## Additional Standard Notices
Please refer to [CDC's Template Repository](https://github.com/CDCgov/template)
for more information about [contributing to this repository](https://github.com/CDCgov/template/blob/master/CONTRIBUTING.md),
[public domain notices and disclaimers](https://github.com/CDCgov/template/blob/master/DISCLAIMER.md),
and [code of conduct](https://github.com/CDCgov/template/blob/master/code-of-conduct.md).
