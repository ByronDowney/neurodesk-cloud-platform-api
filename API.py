"""
This file is the entrypoint for the API. Processes QMENTA context through the "run" method. I am creating this as a
script to translate data into QMENTA/Flywheel data format, but I also intended this to be capable of acting as the
entrypoint for an API container with little to no modification.
"""

import argparse
import subprocess
import os
import random
import string
import json


def run(context):
    """
    QMENTA entrypoint
    """
    # Get the analysis information dictionary (patient id, analysis name...)
    analysis_data = context.fetch_analysis_data()

    # Get the analysis settings (histogram range of intensities)
    settings = analysis_data['settings']

    context.set_progress(message='This is a test of the Neurodesk API')

    file_handler_0 = context.get_files('input_0')[0]
    path_0 = file_handler_0.download(f'/root/input_0/')

    file_handler_1 = context.get_files('input_1')[0]
    path_1 = file_handler_1.download(f'/root/input_1/')


def parse_arguments():
    """
    parses command line arguments for testing or quick data translation
    """
    parser = argparse.ArgumentParser(description='downloads QSMxT to then run it. This is the tool file for the API')
    #parser.add_argument('--container-link', help='link to container repository')
    parser.add_argument('--cloud-platform', help='the name of the cloud platform you are using. Either "QMENTA" or "Flywheel" ')
    parser.add_argument('--generate-settings', help="Path to a generic Neurodesk Application settings file. It will automatically be converted to a format that works with your specified cloud platform")
    return parser.parse_args()


def generate_settings(neurodesk_settings):
    """
    Takes generic Neurodesk settings and converts them to a valid QMENTA settings file.
    """
    name = neurodesk_settings["name"]

    qmenta_settings = []
    qmenta_settings.append({"type": "heading", "content": neurodesk_settings["name"]})
    qmenta_settings.append({"type": "info", "content": (neurodesk_settings["description"] + "<br/> <h3> Inputs: </h3> <br/>")})
    for key, value in neurodesk_settings["config"].items():
        neurodesk_type = value["type"]
        if neurodesk_type == "number":
            neurodesk_type = "decimal"

        input_id = key.replace(" ", "_").replace("-", "_")
        qmenta_settings[1]["content"] = qmenta_settings[1]["content"] + key + ": " + value["description"] + "<br/>"

        qmenta_settings.append({"type": neurodesk_type,
                                "title": key,
                                "id": input_id,
                                "mandatory": int(not value["optional"]),
                                "default": value["default"], #TODO need to fix crash when a value isn't found
                                "min": value["min"],
                                "max": value["max"]
                                })
    for key, value in neurodesk_settings["inputs"].items():
        input_id = key.replace(" ", "_").replace("-", "_")
        qmenta_settings[1]["content"] = qmenta_settings[1]["content"] + key + ": " + value["description"] + "<br/>"

        qmenta_settings.append({"type": "container",
                                "title": key,
                                "id": input_id,
                                "mandatory": int(not value["optional"]),
                                "file_filter": ("c_" + key + "[1,*]<'',[],'\\.*'>"),
                                "in_filter": ["mri_brain_data"],
                                "out_filter": [],
                                "batch": 1,
                                "anchor": 1
                                })

    with open(name + "_settings.json", "w") as settings:
        json.dump(qmenta_settings, settings, indent=4)
        print("QMENTA settings created for ", name)

def generate_manifest(neurodesk_settings):
    """
    Takes generic Neurodesk settings and converts them to a valid Flywheel manifest file.
    """
    name = neurodesk_settings["name"]

    flywheel_settings = {}
    flywheel_settings["name"] = neurodesk_settings["name"].replace(" ", "-").replace("_", "-")
    flywheel_settings["label"] = neurodesk_settings["name"]
    flywheel_settings["description"] = neurodesk_settings["description"]
    flywheel_settings["author"] = neurodesk_settings["author"]
    flywheel_settings["url"] = neurodesk_settings["url"]
    flywheel_settings["source"] = neurodesk_settings["source code"]
    flywheel_settings["license"] = neurodesk_settings["license"]
    flywheel_settings["version"] = neurodesk_settings["version"]
    flywheel_settings["environment"] = neurodesk_settings["environment variables"]
    custom = {"gear-builder": {
        "category": neurodesk_settings["application type"] if neurodesk_settings["application type"] else "analysis",
        "image": neurodesk_settings["image name"]}}
    flywheel_settings["custom"] = custom
    flywheel_settings["config"] = neurodesk_settings["config"]
    inputs = {}
    for key, value in neurodesk_settings["inputs"].items():
        inputs[key] = {
            "base": "file",
            #Todo may not implement this, speak to Steffen "type": {"enum": []},
            "description": value["description"]
        }

    flywheel_settings["inputs"] = inputs


    with open(name + "_manifest.json", "w") as manifest:
        json.dump(flywheel_settings, manifest, indent=4)
        print("Flywheel manifest created for ", name)


def main():
    args = parse_arguments()

    if args.cloud_platform.lower() == "qmenta": #TODO allow for user to specify a list of platforms in the json file?
        if args.generate_settings:
            file = open(args.generate_settings)
            neurodesk_settings = json.load(file)
            generate_settings(neurodesk_settings)

    elif args.cloud_platform.lower() == "flywheel":
        if args.generate_settings:
            file = open(args.generate_settings)
            neurodesk_settings = json.load(file)
            generate_manifest(neurodesk_settings)
    else:
        print('Cloud platform string not recognised. Please use either "QMENTA" or "Flywheel" (upper or lower case does not matter)')


if __name__ == "__main__":
    main()
