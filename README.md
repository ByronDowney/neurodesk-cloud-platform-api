# The Neurodesk Cloud Platform API
This project was created by Byron Downey under the supervision of Steffen Bollmann. It is intended to be an API that allows Neurodesk applications to be run on multiple cloud platforms (currently QMENTA and Flywheel) without requiring a different container for each cloud platform.

# Generic Settings
You will still have to create a generic "Neurodesk" settings file to run your application on a cloud platform. However you only have to do it once in the generic Neurodesk format, and the API will convert the generic format into one that works on your desired cloud platform.

# Using the API
At this stage, the API only creates the required settings/manifest for use in cloud platforms. It does not make your container compatible or provide the necessary entrypoint for each platform. For the required entrypoint for QMENTA, you will need a Python file with a "run" method that parses QMENTA's AnalysisContext variable and an entrypoint.sh file. For Flywheel, you will need a runnable script called "run" (file extension will be dependent on the langauge of the script), and this run file will have to parse the contents of the config.json file at runtime.  

The API can be used from the command line by running the file with Python, as below:  
`python API.py --cloud-platform flywheel --generate-settings example_qsmxt_neurodesk_settings.json`

An example has been provided called run.py for both the QSMxT and CLEAR-SWI neurodesk applications. Run.py contains a run function for QMENTA and another function for Flywheel. Assuming your container has Python 3 installed, an entrypoint.sh can be created for QMENTA by including the following lines in your dockerfile:  
`RUN pip3 install qmenta-sdk-lib`  
`RUN python3 -m qmenta.sdk.make_entrypoint /root/entrypoint.sh /root/`

# Testing the API and Neurodesk Application
Even without logging onto any cloud platform, the function of an application can be testing using a local testing tool. For QMENTA, this is a Python script called "test_tool.py" available from QMENTA and for Flywheel, their CLI is used with an API key available from the Flywheel platform.  

To test locally, first move to the directory containing dockerfile and run it:  
e.g.  
`cd qsmxt_test`  
`docker build -f qsm.Dockerfile . -t byrondowney/public:qsmxt_test1`  

To test locally with QMENTA, move to the folder containing the local testing files, e.g.
For CLEAR-SWI:  
`python test_tool.py byrondowney/public:clearswi-test1 example_data analysis_output --settings CLEAR-SWI_settings.json --values clear-swi_mock_settings_values.json --tool run`  
For QSMxT:  
`Python test_tool.py byrondowney/public:qsmxt_test1 example_data analysis_output --settings QSMxT_settings.json --values QSMxT_mock_settings_values.json --tool run`  

To test locally with Flywheel, first login to the Flywheel CLI with your API key. E.g. if your API key is "12345", run the command:  
`fw login 12345`  
Make sure you are in the v0 directory, e.g. neurodesk-cloud-platform-api\clearswi_test\v0
Then run the local gear test:
For CLEAR-SWI:  
`fw gear local --"Echo Time" "[4,8,12]" --magnitude=input/mag.zip --phase=input/phs.zip`  
For QSMxT:  
`fw gear local --"qsm_iterations" 1 --magnitude=input/mag.zip --phase=input/phs.zip`  

# The Neurodesk Settings
## Notes
1. For the sake of generalisability, we've ignored some niche and less useful features of the cloud platforms, but some are mandatory (such as the PATH variable being needed to run an application in Flywheel)
2. If we add more compatible cloud platforms, we may be forced to add some extra settings for them to work. We will try our best not to break any existing settings files that only use existing cloud platforms, but to use a different cloud platform, you may have to add to/change your Neurodesk settings file.
3. Cloud specific settings/manifest files will just be referred to as "settings" from now on for simplicity. Neurodesk settings will be explicitly called "Neurodesk settings".

## Neurodesk Settings Fields

### platforms (optional)
A list containing the cloud platforms you want to create settings files for. 

### name (required)
The name of the application (this must be unique)

### description (required)
A short description of the application

### author (required)
The author of the application

### url (required)
A link to a relevant URL, e.g. a website where a user could learn more about the application. This can be an empty string.

### source code (required)
A link to the source code. This can be an empty string.

### license (required)
An OSI-approved SPDX license string or 'Other' (https://spdx.org/licenses)

### version (required)
The version of your application e.g. "1.2.3"

### image (required)
The image containing the neurodesk application. To run the application in the cloud, the image must be publicly available through docker hub

### application type (optional)

Either "analysis", "converter", "utility", "classifier", or "qa". This field is only used for Flywheel workflows and
will default to "analysis" if it isn't included in the Neurodesk settings file

### environment variables (optional)

This is required to run a gear on Flywheel, as some environment variables do not carry over. It is recommended to at least copy over your PATH variable as it is critical for many applications. 

### config (required)
Each config is a JSON object that contains multiple fields to give more specificity. Some of these fields are mandatory and others are optional

#### Mandatory config fields
description: A short (ideally 1 sentence) description of this config. This will be displayed to the user.

optional: either "true" if the application sometimes doesn't need this option, or "false" if it is mandatory.

type: The data type of the option. Either "string", "integer", "number" or "boolean"

#### Optional config fields
min: The minimum possible value of the config.

max: The maximum possible value of the config.

default: The default value of the config if a value is not specified.

### inputs (required)
Specifies the types of inputs acceptable for the application. Currently, only files are supported as inputs and like config, each input is a JSON object that contains multiple fields

Currently, input modality (e.g. T1, T2) is not able to be enforced. This could be a feature to implement in the future.

#### Mandatory input fields
description: A short (ideally 1 sentence) description of this input. This will be displayed to the user.

optional: Either "true" if the application sometimes doesn't need this input or "false" if it is mandatory.

#### Optional input fields
file type: A list containing the acceptable file types for this input. Not including this field will allow any file to be used in the application, which you will need to handle.  

A list of Flywheel's file types and their associated file extensions is available here: https://github.com/scitran/core/blob/d4da9eb299db9a7c6c27bdee1032d36db7cef919/api/files.py#L245-L269.  

As QMENTA does not seem to check file type for multiple files in a directory, the preferred option is to tag the directory within the subject in the appropriate file type through the QMENTA client (in the QMENTA client, go to session -> right click -> show files -> select file/directory -> edit metadata -> type tag and press enter, then save).  
The API will tell QMENTA to look for a tag exactly matching the file type(s) that you specify in the Neurodesk settings file, which should also match a Flywheel file type if the application is to be used on both platforms. E.g. if you specify file type as ["dicom"], then QMENTA will be looking for the tag "dicom" which you will need to include for the files that should be used.

### flywheel command (optional)
For Flywheel only, you can explictly provide a command to run in a bash shell. For the QSMxT and CLEARSWI examples, "python run.py" is used to run the script.