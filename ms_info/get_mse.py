import numpy as np
import os
from nipype.utils.filemanip import load_json
from pbr.workflows.nifti_conversion.utils import description_renamer
import pandas as pd
from subprocess import Popen, PIPE
import pandas as pd
import argparse
from os.path import join
import csv
from nipype.utils.filemanip import load_json, json

df = pd.read_csv("/home/sf522915/Documents/msid_missing.csv")


writer = open("/home/sf522915/Documents/msid_mse_check.csv", "w")
spreadsheet = csv.DictWriter(writer, fieldnames=[ "MSID","ExamDate", "mse", "date"])
spreadsheet.writeheader()

for _, row in df.iterrows():
    towrite = {}
    msid = row["msid"]
    msid = msid.replace("ms","")
    msid = msid.lstrip("0")
    #date1 = row["ExamDate"]
  
    cmd = ["ms_get_patient_imaging_exams", "--patient_id", msid, "--dcm_dates"]
    proc = Popen(cmd, stdout=PIPE)
    lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[5:]]
    tmp = pd.DataFrame(lines, columns=["mse", "date"])
    tmp["msid"] = msid
    mse = tmp["mse"]
    date2 = tmp["date"]
    for _, row in tmp.iterrows():
        mse = row["mse"]
        date2 = row["date"]
        print(msid, mse,  date2)
        towrite["MSID"] = msid
        towrite["mse"] = mse
        towrite["ExamDate"] = str(date2)
        towrite["date"] = date2
        spreadsheet.writerow(towrite) 
writer.close()


def get_all_mse(msid):
    cmd = ["ms_get_patient_imaging_exams", "--patient_id", msid]
    proc = Popen(cmd, stdout=PIPE)
    lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[5:]]
    tmp = pd.DataFrame(lines, columns=["mse", "date"])
    tmp["mse"] = "mse"+tmp.mse
    tmp["msid"] = msid
    date = tmp["date"]
    return tmp

"""for idx, row in df.iterrows():
    msid = row.ms
    
    msid = msid.replace("ms", "")
    print(msid)
    
    get_all_mse(msid)"""
