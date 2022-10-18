#!/usr/bin/env python3
import matplotlib

# This backend config avoids $DISPLAY errors in headless machines
matplotlib.use('Agg')

# import matplotlib.pyplot as plt
# import numpy as np
import pdfkit
import subprocess
from subprocess import call
from time import gmtime, strftime
from tornado import template
import glob
from zipfile import ZipFile
import os
from os.path import basename
import json

def flywheel_run():
    # The file that will be initially run by Flywheel. This should run any scripts, QSMxT or otherwise
    print("run.py has started...")

    #takes config and input from config.json
    with open('config.json') as config:
        config = json.load(config)

    echo_times = config["config"]["echo_time"]
    with ZipFile('/flywheel/v0/input/magnitude/mag.zip', 'r') as zipObj:
        zipObj.extractall('/flywheel/v0/input/magnitude/')

    with ZipFile('/flywheel/v0/input/phase/phs.zip', 'r') as zipObj:
        zipObj.extractall('/flywheel/v0/input/phase/')

    print("Echo Times:  ", echo_times)

    print("Sorting DICOM data...")
    call([
        "python3",
        "/opt/QSMxT/run_0_dicomSort.py",
        "/flywheel/v0/input",  # input - this should be in the Flywheel input folder!
        "/00_dicom",
        ])

    ima_files = glob.glob("/00_dicom/**/*.IMA", recursive=True)
    print('found ' + str(len(ima_files)) + ' ima_files after Sorting DICOM data in /00_dicom')
    print("Converting DICOM data...")

    try:
        retcode = call([
            "python3",
            "/opt/QSMxT/run_1_dicomToBids.py",
            "/00_dicom/",
            "/01_bids"
        ])
        if retcode < 0:
            print("Converting DICOM data was terminated by signal" + str(retcode))
        else:
            print("Converting DICOM data returned " + str(retcode))
    except Exception as e:
        print("Converting DICOM data failed:" + e)
        raise

    nii_files = glob.glob("/01_bids/**/*.nii.gz", recursive=True)
    print('found ' + str(len(nii_files)) + ' nii_files after Converting DICOM data in /01_bids')

    print('Run CLEAR-SWI ...')

    CompletedProcess = subprocess.run([
            "julia",
            "/root/clearswi.jl",
            echo_times
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')

    print('CLEARSWI stdout: ' + CompletedProcess.stdout)
    print('CLEARSWI stderr: ' + CompletedProcess.stderr)

    output_file = glob.glob("/root/clearswi_output/*.nii")
    print('outputfile is ... ' + output_file[0])
    print('Zipping and moving files to the output directory...')

    # create a ZipFile object
    with ZipFile('/flywheel/v0/output/output.zip', 'w') as zipObj:
       # Iterate over all the files in directory
       for folderName, subfolders, filenames in os.walk("/root/clearswi_output/"):
           for filename in filenames:
               #create complete filepath of file in directory
               filePath = os.path.join(folderName, filename)
               # Add file to zip
               zipObj.write(filePath, basename(filePath))

    print('Exiting...')

    exit(0)

# AnalysisContext documentation: https://docs.qmenta.com/sdk/sdk.html
def run(context):
    # Get the analysis information dictionary (patient id, analysis name...)
    analysis_data = context.fetch_analysis_data()

    # Get the analysis settings (histogram range of intensities)
    settings = analysis_data['settings']
    context.set_progress(message=f"Analysis data: {analysis_data}")
    context.set_progress(message=f"Qmenta settings: {settings}")

    context.set_progress(message='Running CLEAR-SWI')

    file_handler_0 = context.get_files('magnitude')[0]
    path_0 = file_handler_0.download(f'/root/magnitude/')

    file_handler_1 = context.get_files('phase')[0]
    path_1 = file_handler_1.download(f'/root/phase/')

    echo_times = settings["echo_time"]

    context.set_progress(message='Sorting DICOM data...')
    call([
        "python3",
        "/opt/QSMxT/run_0_dicomSort.py",
        "/root/",
        "/00_dicom"
    ])

    ima_files = glob.glob("/00_dicom/**/*.IMA", recursive=True)
    context.set_progress(message='found ' + str(len(ima_files)) + ' ima_files after Sorting DICOM data in /00_dicom')

    context.set_progress(message='Converting DICOM data...')
    try:
        retcode = call([
            "python3",
            "/opt/QSMxT/run_1_dicomToBids.py",
            "/00_dicom/",
            "/01_bids"
        ])
        if retcode < 0:
            context.set_progress(message="Converting DICOM data was terminated by signal" + str(retcode))
        else:
            context.set_progress(message="Converting DICOM data returned " + str(retcode))
    except Exception as e:
        context.set_progress(message="Converting DICOM data failed:" + e)
        raise

    nii_files = glob.glob("/01_bids/**/*.nii.gz", recursive=True)
    context.set_progress(message='found ' + str(len(nii_files)) + ' nii_files after Converting DICOM data in /01_bids')

    context.set_progress(message='Run CLEARSWI ...')

    CompletedProcess = subprocess.run([
        "julia",
        "clearswi.jl",
        echo_times
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
    context.set_progress(message='CLEARSWI stdout: ' + CompletedProcess.stdout)
    context.set_progress(message='CLEARSWI stderr: ' + CompletedProcess.stderr)

    output_file = glob.glob("/root/clearswi_output/*.nii")
    context.set_progress(message='outputfile is ... ' + output_file[0])

    # Upload the results
    context.set_progress(message='Uploading results...')

    for i in range(len(output_file)):
        context.upload_file(output_file[i], f'output_{i}.nii')


if __name__ == "__main__":
    flywheel_run()
