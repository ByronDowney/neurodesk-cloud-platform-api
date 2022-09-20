# The Neurodesk Cloud Platform API
This project was created by Byron Downey under the supervision of Steffen Bollmann. It is intended to be an API that allows Neurodesk applications to be run on multiple cloud platforms (currently QMENTA and Flywheel) without needing to modify the containers to work specifically with each platform.

# Generic Settings
You will still have to create a settings file to run your application on a cloud platform. However you only have to do it once in the generic Neurodesk format, and the API will convert the generic format into one that works on your desired cloud platform.

# #TODO CHANGE THIS AS I WORK ON THE API
You also do not need to do anything to your container, as this "API" is currently just a script that creates the necessary settings/manifest file to run your application on a cloud platform.

#The Generic Neurodesk Setting
## Notes
1. For the sake of generalisability, we've ignored some niche and less useful features of the cloud platforms, but some are mandatory (such as the PATH variable being needed to run an application in Flywheel)
2. If we add more compatible cloud platforms, we may be forced to add some extra settings for them to work. We will try our best not to break any existing settings files that only use existing cloud platforms, but to use a different cloud platform, you may have to add to/change your Neurodesk settings file.

## Settings Fields

### name
The name of the application (this must be unique)

### description
A short description of the application

### author
The author of the application

### url

### source code

### license
An OSI-approved SPDX license string or 'Other' (https://spdx.org/licenses)

### version

### application type

Either "analysis", "converter", "utility", "classifier", or "qa". This field is only used for Flywheel workflows and
will default to "analysis" if it isn't included in the settings file

### #TODO - I think it just overrides PATH? environment variables

This is required to run a gear on Flywheel, as some environment variables do not carry over 

### config
Each configuration option contains multiple fields to give more specificity. Some of these options are mandatory and others are optional

#### Mandatory config fields
description: A short (ideally 1 sentence) description of this option

optional: either "true" if the application sometimes doesn't need this option, or "false" if it is mandatory.

type: The data type of the option. Either string, integer, number or boolean

min: The minimum possible value of the option.

max: The maximum possible value of the option.

default: The default value of the option if a value is not specified.

#### Optional config fields

### inputs
Specifies the types of inputs acceptable for the application. Currently, only files are supported as inputs.

data type: #TODO TALK WITH STEFFEN - SHOULD I BE DOING THIS The type of data contained in the input. Currently, the options are: "nifti", "dicom"

modality: Currently, modality (e.g. T1, T2) is not enforced. This could be a feature to expand on in the future.
