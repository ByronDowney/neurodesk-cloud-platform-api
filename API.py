"""
A script to run to convert a general Neurodesk settings file to a cloud specific one. Either specify the cloud platform
through a command line argument or in your Neurodesk settings file.
"""

import argparse
import subprocess
import os
import random
import string
import json


def parse_arguments():
    """
    Parses command line arguments
    """
    parser = argparse.ArgumentParser(description='downloads QSMxT to then run it. This is the tool file for the API')
    parser.add_argument('--cloud-platform', help='the name of the cloud platform you are using. Either "QMENTA" or "Flywheel" ')
    parser.add_argument('--generate-settings', help="Path to a generic Neurodesk Application settings file. It will automatically be converted to a format that works with your specified cloud platform")
    return parser.parse_args()


def generate_settings(neurodesk_settings):
    """
    Takes generic Neurodesk settings and converts them to a valid QMENTA settings file.
    """
    name = neurodesk_settings["name"]
    try:
        qmenta_settings = []
        qmenta_settings.append({"type": "heading", "content": neurodesk_settings["name"]})
        qmenta_settings.append({"type": "info", "content": (neurodesk_settings["description"] + "<br/> <h3> Inputs: </h3> <br/>")})

        for key, value in neurodesk_settings["config"].items():
            neurodesk_type = value["type"]
            if neurodesk_type == "number":
                neurodesk_type = "decimal"

            input_id = key.replace(" ", "_").replace("-", "_")
            qmenta_settings[1]["content"] = qmenta_settings[1]["content"] + key + ": " + value["description"] + "<br/>"

            qmenta_settings.append({
                # uses dictionary unpacking ("**" syntax) to conditionally
                # add optional values if they exist in the general neurodesk settings file
                "type": neurodesk_type,
                "title": key,
                "id": input_id,
                **({"mandatory": int(not value["optional"])} if "mandatory" in value else {}),
                **({"default": value["default"]} if "default" in value else {}),
                **({"min": value["min"]} if "min" in value else {}),
                **({"max": value["max"]} if "max" in value else {})
                })
        for key, value in neurodesk_settings["inputs"].items():
            input_id = key.replace(" ", "_").replace("-", "_")
            qmenta_settings[1]["content"] = qmenta_settings[1]["content"] + key + ": " + value["description"] + "<br/>"

            qmenta_settings.append({
                # uses dictionary unpacking ("**" syntax) to conditionally
                # add optional values if they exist in the general neurodesk settings file and to define default values
                "type": "container",
                "title": key,
                "id": input_id,
                "mandatory": int(not value["optional"]),
                **({"file_filter": "c_" + key + "[1,*]<'', any ['" + "', '".join(value["file type"]) +"']>"} if "file type" in value else {"file_filter": "c_" + key + "[1,*]<''>"}),
                "in_filter": ["mri_brain_data"],
                "out_filter": [],
                **({"batch": int(value["batch"])} if "batch" in value else {"batch": 1}),
                **({"anchor": int(value["anchor"])} if "anchor" in value else {"anchor": 1})
                })

        with open(name + "_settings.json", "w") as settings:
            json.dump(qmenta_settings, settings, indent=4)
            print("A QMENTA settings file has been created for", name, "at", os.path.join(os.getcwd(), name + "_settings.json"))
    except KeyError as e:
        print("Error: to generate a QMENTA settings file you must include "
              "the following field in your neurodesk settings file:\n ", e.args[0])


def generate_manifest(neurodesk_settings):
    """
    Takes generic Neurodesk settings and converts them to a valid Flywheel manifest file.
    """
    try:
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
        if "environment variables" in neurodesk_settings:
            flywheel_settings["environment"] = neurodesk_settings["environment variables"]
        custom = {"gear-builder": {
            "category": neurodesk_settings["application type"] if "application type" in neurodesk_settings else "analysis",
            "image": neurodesk_settings["image"]}
        }
        flywheel_settings["custom"] = custom
        flywheel_settings["config"] = neurodesk_settings["config"]
        inputs = {}
        for key, value in neurodesk_settings["inputs"].items():
            inputs[key] = {
                "base": "file",
                "type": {"enum": value["file type"]},
                "description": value["description"]
            }

        flywheel_settings["inputs"] = inputs
        if "flywheel command" in neurodesk_settings:
            flywheel_settings["command"] = neurodesk_settings["flywheel command"]
    except KeyError as e:
        print("Error: to generate a Flywheel manifest file you must include "
              "the following field in your neurodesk settings file:\n ", e.args[0])

    with open(name + "_manifest.json", "w") as manifest:
        json.dump(flywheel_settings, manifest, indent=4)
        print("A Flywheel manifest file has been created for", name, "at", os.path.join(os.getcwd(), name + "_manifest.json"))

def main():
    args = parse_arguments()

    if args.cloud_platform:
        if args.cloud_platform.lower() == "qmenta":
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
    else:
        # allows the user to include a list of platforms to create cloud specific settings files for, instead of
        # specifying as an argument. Specifying a platform as an CLI argument takes precedence over the "platforms"
        # value in the  settings file
        if args.generate_settings:
            file = open(args.generate_settings)
            neurodesk_settings = json.load(file)
            platforms = neurodesk_settings["platforms"] if "platforms" in neurodesk_settings else ["nothing"]
            for platform in platforms:
                if platform.lower() == "qmenta":
                    generate_settings(neurodesk_settings)
                elif platform.lower() == "flywheel":
                    generate_manifest(neurodesk_settings)
                elif platform.lower() == "nothing":
                    print("No cloud platform was specified so no files have been created. Please specify a cloud "
                          "platform via argument or optionally in the Neurodesk settings file")

if __name__ == "__main__":
    main()
