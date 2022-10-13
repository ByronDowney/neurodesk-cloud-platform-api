# The Neurodesk Cloud Platform API
This project was created by Byron Downey under the supervision of Steffen Bollmann. It is intended to be an API that allows Neurodesk applications to be run on multiple cloud platforms (currently QMENTA and Flywheel) without requiring a different container for each cloud platform.

# Generic Settings
You will still have to create a generic "Neurodesk" settings file to run your application on a cloud platform. However you only have to do it once in the generic Neurodesk format, and the API will convert the generic format into one that works on your desired cloud platform.

# Using the API
At this stage, the API only creates the required settings/manifest for use in cloud platforms. It does not make your container compatible or provide the necessary entrypoint for each platform. For the required entrypoint for QMENTA, you will need a python file with a "run" method that parses QMENTA's AnalysisContext variable and an entrypoint.sh file. For Flywheel, you will need a runnable script called "run" (file extension will be dependent on the langauge of the script), and this run file will have to parse the contents of the config.json file at runtime.

An example has been provided called run.py for both the QSMxT and CLEAR-SWI neurodesk applications. Run.py contains a run function for QMENTA and another function for Flywheel. Assuming your container has python3 installed, an entrypoint.sh can be created for QMENTA by including the following lines in your dockerfile:  
RUN pip3 install qmenta-sdk-lib  
RUN python3 -m qmenta.sdk.make_entrypoint /root/entrypoint.sh /root/  

#The Generic Neurodesk Setting
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

### application type (optional)

Either "analysis", "converter", "utility", "classifier", or "qa". This field is only used for Flywheel workflows and
will default to "analysis" if it isn't included in the Neurodesk settings file

### environment (optional)

This is required to run a gear on Flywheel, as some environment variables do not carry over. It is recommended to at least copy over your PATH variable as it is critical for many applications. 

### config (required)
Each config is a JSON object that contains multiple fields to give more specificity. Some of these fields are mandatory and others are optional

#### Mandatory config fields
description: A short (ideally 1 sentence) description of this config

optional: either "true" if the application sometimes doesn't need this option, or "false" if it is mandatory.

type: The data type of the option. Either "string", "integer", "number" or "boolean"

#### Optional config fields
min: The minimum possible value of the config.

max: The maximum possible value of the config.

default: The default value of the config if a value is not specified.

### inputs (required)
Specifies the types of inputs acceptable for the application. Currently, only files are supported as inputs.

data type: #TODO TALK WITH STEFFEN - SHOULD I BE DOING THIS The type of data contained in the input.

modality: Currently, modality (e.g. T1, T2) is not enforced. This could be a feature to expand on in the future.

Like config, each input is a JSON object that contains multiple fields

#### Mandatory input fields
data type: A list containing the acceptable data types for this input. Currently, the options are: "nifti" and "dicom"

#### Optional input fields
optional: either "true" if the application sometimes doesn't need this input or "false" if it is mandatory.

### flywheel command
For Flywheel only, you can explictly provide a command to run in a bash shell. For the QSMxT and CLEARSWI examples, "python run.py" is used to run the script.