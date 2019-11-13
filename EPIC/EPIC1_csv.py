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

df = pd.read_csv("/home/sf522915/csv/EPIC1FINAL_ADAMSLIST.csv")

"""def _get_output(mse):
    mse_num = int(mse.replace("mse", ""))
    if mse_num <= 4500:
        output_dir = '/data/henry7/PBR/subjects'
    else:
        output_dir = '/data/henry11/PBR/subjects'
    return output_dir"""



writer = open("/home/sf522915/EPIC1_FINAL_ADAMSLIST_WITHMSE.csv", "w")
spreadsheet = csv.DictWriter(writer, fieldnames=["msID", "mseID", "EPIC_Project", "VisitType", "Brain_MRI_Date","scanner",\
                                                "Jan2018_Date", "SIENAX_Status", "sienax_flair", "sienax_t2", "T1", "T2", "FLAIR", \
                                                 "vscale",
                                                 "brain vol (u, mm3)",
                                                 "WM vol (u, mm3)",
                                                 "GM vol (u, mm3)",
                                                 "vCSF vol (u, mm3)",
                                                 "cortical vol (u, mm3)",
                                                 "lesion vol (u, mm3)" ])
spreadsheet.writeheader()


for _, row in df.iterrows():
    msid = row['msID']
    msid = "ms" + msid.replace("ms", "").lstrip("0")
    print(msid)
    date1 = int(row['Brain_MRI_Date'])
    EPIC = row["EPIC_Project"]
    visit = row["VisitType"]
    project = row["EPIC_Project"]
    jan = row["Jan2018_Date"]
    sienax = row["SIENAX_Status"]
    mse = ""
    sienax_flair = ""
    sienax_t2 = ""
    t1_file = ""
    t2_file = ""
    flair_file = ""
    vscale = ""
    brain = ""
    wm = ""
    gm = ""
    csf = ""
    cortical = ""
    lesion = ""
    scanner = ""




    #row = {"msID": msid, "EPIC_Project": project, "VisitType": visit,\
          # "Brain_MRI_Date": date1, "Jan2018_Date": jan, "SIENAX_Status": sienax, "mseID": ""}

    #print(row)

    cmd = ["ms_get_patient_imaging_exams", "--patient_id", msid.replace("ms", ""), "--dcm_dates"]
    proc = Popen(cmd, stdout=PIPE)
    lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[5:]]
    #print(cmd)
    tmp = pd.DataFrame(lines, columns=["mse", "date"])
    tmp["msid"] = msid
    mse = tmp["mse"]
    date2 = tmp["date"]

    for _, row in tmp.iterrows():
        mse = row["mse"]
        date2 = row["date"]
        if str(date1) == (date2):

            mse = str("mse" + mse)
            print(mse)
            #print(date1, date2, msid, mse, EPIC, visit)
            if os.path.exists(_get_output(mse)+ "/" + mse + "/sienax_flair"):
                sienax_flair = "sienax_flair"
                list = os.listdir(_get_output(mse)+'/'+mse+"/sienax_flair/") # dir is your directory path
                number_files = len(list)
                if number_files > 30:
                    report = os.path.join(_get_output(mse), mse, "sienax_flair/report.sienax")
                    with open(report, "r") as f:
                        lines = [line.strip() for line in f.readlines()]
                        for line in lines:
                            if line.startswith("VSCALING"):
                                vscale =  line.split()[1]
                                #print("...its working")
                            elif line.startswith("pgrey"):
                                cortical = line.split()[2]
                            elif line.startswith("vcsf"):
                                csf = line.split()[2]
                            elif line.startswith("GREY"):
                                gm = line.split()[2]
                            elif line.startswith("WHITE"):
                                wm = line.split()[2]
                            elif line.startswith("BRAIN"):
                                brain = line.split()[2]

                    lm = os.path.join(_get_output(mse), mse, "sienax_flair/lesion_mask.nii.gz")
                    img = nib.load(lm)
                    data = img.get_data()
                    lesion = np.sum(data)




            if os.path.exists(_get_output(mse) + "/" + mse + "/sienax_t2"):
                sienax_t2 = "sienax_t2"
                list = os.listdir(_get_output(mse)+ '/' + mse + "/sienax_t2/") # dir is your directory path
                number_files = len(list)
                if number_files > 30:
                    report = os.path.join(_get_output(mse), mse, "sienax_t2/report.sienax")
                    with open(report, "r") as f:
                        lines = [line.strip() for line in f.readlines()]
                        for line in lines:
                            if line.startswith("VSCALING"):
                                vscale =  line.split()[1]
                                #print("...its working")
                            elif line.startswith("pgrey"):
                                cortical = line.split()[2]
                            elif line.startswith("vcsf"):
                                csf = line.split()[2]
                            elif line.startswith("GREY"):
                                gm = line.split()[2]
                            elif line.startswith("WHITE"):
                                wm = line.split()[2]
                            elif line.startswith("BRAIN"):
                                brain = line.split()[2]

                            """if line.startswith("VSCALING"):
                                row["vscale"] =  line.split()[1]
                                print("...its working")
                            elif line.startswith("pgrey"):
                                row["cortical vol (u, mm3)"] = line.split()[2]
                            elif line.startswith("vcsf"):
                                row["vCSF vol (u, mm3)"] = line.split()[2]
                            elif line.startswith("GREY"):
                                row["GM vol (u, mm3)"] = line.split()[2]
                            elif line.startswith("WHITE"):
                                row["WM vol (u, mm3)"] = line.split()[2]
                            elif line.startswith("BRAIN"):
                                row["brain vol (u, mm3)"] = line.split()[2]"""

                    lm = os.path.join(_get_output(mse), mse, "sienax_t2/lesion_mask.nii.gz")
                    img = nib.load(lm)
                    data = img.get_data()
                    lesion = np.sum(data)

            if not os.path.exists(_get_output(mse)+"/"+mse+"/alignment/status.json"):
                #row = {"sienax_flair": "none", "sienax_t2": "none", "T1": "none", "T2": "none", "FLAIR": "none"}
                continue

            with open(_get_output(mse)+"/"+mse+"/alignment/status.json") as data_file:
                data = json.load(data_file)
            if len(data["t1_files"]) == 0:
                continue
                #row = {"T1": "NONE - probably spinal cord"}
            else:
                t1_file = data["t1_files"][-1]
                t1_file = (t1_file.split('/')[-1])
                mseID = t1_file.split("-")[1]
                #row = {"T1": t1_file}
                series = t1_file.split("-")[2].lstrip("0")
                if not len(series) > 0:
                    series = "1"
                dcm = glob("/working/henry_temp/PBR/dicoms/{0}/E*/{1}/*.DCM".format(mse,series))
                if len(dcm) > 0 :
                    dcm = dcm[0]
                    cmd = ["dcmdump", dcm]
                    proc = Popen(cmd, stdout=PIPE)
                    lines = str([l.decode("utf-8").split() for l in proc.stdout.readlines()[:]])
                    row["scanner"] = lines
                    if "qb3-3t" in lines:
                        #print("qb3-3t")
                        scanner = "qb3"
                    elif "SIEMENS" in lines:
                        #print("SIEMENS")
                        scanner = "Skyra"
                    elif "CB3TMR"  or "CB-3TMR" in lines:
                        #print("CB3TMR")
                        scanner = "CB"
                    else:
                        scanner = "unknown"


            if len(data["t2_files"]) == 0:
                row = {"T2": "NONE"}
            else:
                t2_file = data["t2_files"][-1]
                t2_file = (t2_file.split('/')[-1])
                row = {"T2": t2_file}
                #print(t2_file)

            if len(data["flair_files"]) == 0:
                row = {"FLAIR": "NONE"}

            else:
                flair_file = data["flair_files"][-1]
                flair_file = (flair_file.split('/')[-1])
                row = {"FLAIR": flair_file}
                #print(flair_file)


    row = {"msID": msid, "mseID": mseID, "EPIC_Project": project, "VisitType": visit,\
            "Brain_MRI_Date": date1,"scanner": scanner, "Jan2018_Date": jan, "SIENAX_Status": sienax,\
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