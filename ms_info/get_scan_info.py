import csv
import os
import pbr
from pbr.base import _get_output
import pandas as pd
import argparse
from subprocess import check_output, check_call, Popen, PIPE
from getpass import getpass
import json
from nipype.utils.filemanip import load_json
heuristic = load_json(os.path.join(os.path.split(pbr.__file__)[0], "heuristic.json"))["filetype_mapper"]
from pbr.workflows.nifti_conversion.utils import description_renamer
from glob import glob

password = getpass("mspacman password: ")
check_call(["ms_dcm_echo", "-p", password])

def get_align(mse):
    align = _get_output(mse)+"/"+mse+"/alignment/status.json"
    return align


def filter_files(descrip,nii_type, heuristic):
    output = []
    for i, desc in enumerate(descrip):
        if desc in list(heuristic.keys()):
            if heuristic[desc] == nii_type:
                 output.append(desc)
    return output

def get_scanner_info(c, out):

    df = pd.read_csv("{}".format(c))

    for idx in range(len(df)):
        msid = df.loc[idx, 'msid']
        mse = df.loc[idx,'mse']
        print(msid, mse)


        if os.path.exists(get_align(mse)):

            with open(get_align(mse)) as data_file:
                data = json.load(data_file)
            if len(data["t1_files"]) > 0:
                t1_file = data["t1_files"][-1].split('/')[-1]
                df.loc[idx,"T1"] = t1_file
            if len(data["t2_files"]) > 0:
                t2_file = data["t2_files"][-1].split('/')[-1]
                df.loc[idx,"T2"] = t2_file
            if len(data["flair_files"]) > 0:
                flair_file = data["flair_files"][-1].split('/')[-1]
                df.loc[idx,"FLAIR"] = flair_file

        num = mse.split("mse")[-1]
        print("ms_dcm_exam_info", "-t", num, "-D")
        cmd = ["ms_dcm_exam_info", "-t", num, "-D"]
        proc = Popen(cmd, stdout=PIPE)
        lines = [description_renamer(" ".join(l.decode("utf-8").split()[1:-1])) for l in proc.stdout.readlines()[8:]]
        sequences  = ["T1", "T2", "FLAIR", "T1_Gad"]
        for sq in sequences:
            nii_type = sq
            if nii_type:
                try:
                    sequence_name = filter_files(lines, nii_type, heuristic)[-1]
                    df.loc[idx, format(sq)] =sequence_name
                    print(sequence_name, " is the {0}".format(sq))
                except:
                    pass
        try:
            dicom = glob("/working/henry_temp/PBR/dicoms/{0}/E*/*/*.DCM".format(mse))[0]
            cmd = ["dcmdump", dicom]
            proc = Popen(cmd, stdout=PIPE)
            output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
            x = ["SoftwareVersions", "BodyPartExamined", "StationName", "TransmitCoilName", "ReceiveCoilName"]
            for line in output:
                for flag in x:
                    if flag in line:

                        dicom_info = str(str(line[2:]).split(']')[0].split('[')[2:]).replace('[',"").replace(']','').replace('"','').replace("'","")
                        print(flag,":", dicom_info)

                        if flag == "SoftwareVersions":
                            df.loc[idx,"SoftwareVersions"] = dicom_info
                        if flag == "BodyPartExamined":
                            df.loc[idx,"BodyPartExamined"] = dicom_info
                        if flag == "StationName":
                            df.loc[idx,"StationName"] = dicom_info
                        if flag == "TransmitCoilName":
                            df.loc[idx,"TransmitCoilName"] = dicom_info
                        if flag == "ReceiveCoilName":
                            df.loc[idx,"ReceiveCoilName"] = dicom_info

        except:
            df.loc[idx, "dicom"] = "no dicom in working directory"
            pass

       
        df.to_csv("{0}".format(out))



if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code allows you to grab siena values given a csv (with mse and msid) and an output csv')
    parser.add_argument('-i', help = 'csv containing the msid and mse')
    parser.add_argument('-o', help = 'output csv')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    out = args.o
    print(c, out)
    get_scanner_info(c, out)

