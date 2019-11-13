import csv
import os
import pbr
from pbr.base import _get_output
import pandas as pd
import argparse
import json
import numpy as np
import nibabel as nib
from pbr.base import _get_output
from glob import glob
from subprocess import Popen, PIPE

mses = ["mse4530", "mse2282", "mse2464"]

def extract_dicom(x):
    if x in line:
        #print(line)
        dicom_info = str(str(line[2:]).split(']')[0].split('[')[2:]).replace('[',"").replace(']','').replace('"','').replace("'","")
        print(x,":", dicom_info)


for mse in mses:
    dicom = ""
    try:
        dicom = glob("/working/henry_temp/PBR/dicoms/{0}/E*/*/*.DCM".format(mse))[0]
    except:
        pass
    if len(dicom) > 1:
        print("***************************")
        print(mse)
        cmd = ["dcmdump", dicom]
        proc = Popen(cmd, stdout=PIPE)
        output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
        for line in output:
            extract_dicom("SoftwareVersions")
            extract_dicom("BodyPartExamined")
            extract_dicom("StationName")
            extract_dicom("ReceiveCoilName")
            extract_dicom("Coil")
            extract_dicom("TransmitCoilName")
