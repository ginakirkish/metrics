from glob import glob
import pandas as pd
import numpy as np
import csv
import os
import matplotlib.pyplot as plt
from subprocess import check_output
from subprocess import Popen, PIPE
import shutil
import itertools
from getpass import getpass
from subprocess import check_call
import pbr
from pbr.base import _get_output
import json
import nibabel as nib

df = pd.read_csv("/home/sf522915/EPIC1FINAL_ADAMLIST_list2_missing_acc.csv")

"""def _get_output(mse):
    mse_num = int(mse.replace("mse", ""))
    if mse_num <= 4500:
        output_dir = '/data/henry7/PBR/subjects'
    else:
        output_dir = '/data/henry11/PBR/subjects'
    return output_dir"""



writer = open("/home/sf522915/EPIC1_FINAL_ADAMSLIST_WITHMSE_list2_new.csv", "w")
spreadsheet = csv.DictWriter(writer, fieldnames=["msID", "mseID","Accession_Number", "EPIC_Project", "VisitType", "Brain_MRI_Date","scanner",\
                                                 "sienax_flair", "sienax_t2", "T1", "T2", "FLAIR", \
                                                 "vscale",
                                                 "brain vol (u, mm3)",
                                                 "WM vol (u, mm3)",
                                                 "GM vol (u, mm3)",
                                                 "vCSF vol (u, mm3)",
                                                 "cortical vol (u, mm3)",
                                                 "lesion vol (u, mm3)" ])
spreadsheet.writeheader()


for _, row in df.iterrows():
    acc = row["Accession_Number"]
    msid = row['msID']
    msid = "ms" + msid.replace("ms", "").lstrip("0")
    print(msid)
    date1 = int(row['Brain_MRI_Date'])
    print(date1)
    EPIC = row["EPIC_Project"]
    visit = row["VisitType"]
    project = row["EPIC_Project"]
    mse = ""
    sienax_flair = "none"
    sienax_t2 = "none"
    t1_file = "none"
    t2_file = "none"
    flair_file = "none"
    vscale = "none"
    brain = "none"
    wm = "none"
    gm = "none"
    csf = "none"
    cortical = "none"
    lesion = "none"
    scanner = "none"

    cmd = ["ms_get_exam_id", "-a", acc]
    proc = Popen(cmd, stdout=PIPE)
    lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
    #print(lines)
    mse = "mse" + str(lines[5][1])
    print(mse, _get_output(mse)+ "/" + mse + "/sienax_flair" )
    print(acc)
    print(mse, "THIS IS THE MSE", msid)


    row = {"msID": msid, "mseID": mse,  "EPIC_Project": project, "VisitType": visit,"Accession_Number": acc,\
            "Brain_MRI_Date": date1,"scanner": scanner,\
            "sienax_flair" : sienax_flair, "sienax_t2": sienax_t2, "T1": t1_file, "T2": t2_file, "FLAIR": flair_file, \
            "vscale": vscale,
            "brain vol (u, mm3)": brain,
            "WM vol (u, mm3)" : wm,
            "GM vol (u, mm3)": gm,
            "vCSF vol (u, mm3)": csf,
            "cortical vol (u, mm3)": cortical,
            "lesion vol (u, mm3)": lesion}

    spreadsheet.writerow(row)
writer.close()