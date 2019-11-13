from glob import glob
import pandas as pd
import numpy as np
import csv
import os
from subprocess import Popen, PIPE
from pbr.base import _get_output
import json
import nibabel as nib

df = pd.read_csv("/home/sf522915/Documents/simone_siena.csv")

writer = open("/home/sf522915/Documents/summit_siena_data.csv", "w")
spreadsheet = csv.DictWriter(writer, fieldnames=["msID", "mse", "VisitType",
                                                 "PBVC", "T1_mse1", "T1_mse2"])
spreadsheet.writeheader()


for _, row in df.iterrows():
    bl_mse = "mse" +  str(int(row["mse1"]))
    tp1_mse = "mse" + str(int(row["mse2"]))
    msid ="ms" + str(row["msid"])
    mse1 = bl_mse
    mse2 = tp1_mse
    siena1 = ""
    pbvc = ""
    try:
        siena1 = glob("/data/henry10/PBR_long/subjects/{0}/siena_optibet/*{1}*{2}*".format(msid,mse1, mse2))[0]
    except:
        pass

    print(msid, mse1,mse2)

    siena_report = siena1 + "/report.siena"
    if os.path.exists(siena_report):
        print(siena_report)
        with open(siena_report, "r") as f:
            lines = [line.strip() for line in f.readlines()]
            for line in lines:
                if line.startswith("finalPBVC"):
                    pbvc =  line.split()[1]
                    print(pbvc, "FINAL PBVC")

    if os.path.exists(_get_output(mse1)+"/"+mse1+"/nii/status.json"):

        with open(_get_output(mse1)+"/"+mse1+"/nii/status.json") as data_file:
            data = json.load(data_file)
        if len(data["t1_files"]) == 0:
            t1_file1 = "none"
            print(t1_file1)
        else:
            t1_file1 = data["t1_files"][-1]
            t1_file1 = t1_file1.split("/")[-1]
            print(t1_file1)

    if os.path.exists(_get_output(mse2)+"/"+mse2+"/nii/status.json"):
        with open(_get_output(mse2)+"/"+mse2+"/nii/status.json") as data_file:
            data = json.load(data_file)
        if len(data["t1_files"]) == 0:
            t1_file2 = "none"
            print(t1_file2)
        else:
            t1_file2 = data["t1_files"][-1]
            t1_file2 = t1_file2.split("/")[-1]
            print(t1_file2)



    row = {"msID" : msid, "VisitType" : "mse1_mse2", "mse": mse1 + "_" + mse2, "PBVC": pbvc, "T1_mse1": t1_file1, "T1_mse2": t1_file2}



    spreadsheet.writerow(row)
writer.close()