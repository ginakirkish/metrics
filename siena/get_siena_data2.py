from subprocess import check_output, check_call
from getpass import getpass
import nibabel as nib
import numpy as np
from glob import glob
import csv
import os
import pandas as pd
from pbr.base import _get_output
import json
from subprocess import Popen, PIPE


#password = getpass("mspacman password: ")
#check_call(["ms_dcm_echo", "-p", password])

folders = sorted(glob("ms*"))

writer = open("/home/sf522915/siena_data_pbr.csv", "w")
spreadsheet = csv.DictWriter(writer, 
                             fieldnames=["msid", "Scan Date", "Scan Status",
                                        "vscale", 
                                        "brain vol (u, mm3)",
                                        "WM vol (u, mm3)", 
                                        "GM vol (u, mm3)",
                                        "vCSF vol (u, mm3)",
                                        "cortical vol (u, mm3)",
                                        "lesion vol (u, mm3)", "mse1","mse2", "t1_file1", "t1_file2", "error"])
spreadsheet.writeheader()

df = pd.read_csv("/home/sf522915/Documents/msid.csv")

ind = 0 
for _, row in df.iterrows():
    msid = row["msid"]
    msid = "/data/henry6/mindcontrol_ucsf_env/watchlists/long/VEO/gina/" + msid + ".txt"
    ind = 0 
    with open(msid) as f:

        content = f.read().splitlines()
        size = len(content) -1
        index = 0
        while index < size:
            index += 1
            print(row["msid"], content[index-1], content[index])
            mse1 = content[index-1]
            mse2 = content[index]

            if not os.path.exists(_get_output(mse1)+"/"+mse1+"/alignment/status.json") or \
            not os.path.exists(_get_output(mse2)+"/"+mse2+"/alignment/status.json"):
                continue

            with open(_get_output(mse1)+"/"+mse1+"/alignment/status.json") as data_file:
                data = json.load(data_file)
            if len(data["t1_files"]) == 0:
                t1_file1 = "none"

            else:
                t1_file1 = data["t1_files"][-1]
                t1_file1 = t1_file1.split("alignment")[0] + "alignment/baseline_mni/" + \
                t1_file1.split('/')[-1].split('.')[0] + "_T1mni.nii.gz"

            with open(_get_output(mse2)+"/"+mse2+"/alignment/status.json") as data_file:
                data = json.load(data_file)
            if len(data["t1_files"]) == 0:
                t1_file2 = "none"

            else:
                t1_file2 = data["t1_files"][-1]
                t1_file2 =  t1_file2.split("alignment")[0] + "alignment/baseline_mni/" + \
                t1_file2.split('/')[-1].split('.')[0] + "_T1mni.nii.gz"

            if not os.path.exists("/data/henry11/PBR_long/subjects/" + os.path.split(msid)[-1].split(".txt")[0]+ '/' + mse1 + '_to_' + mse2):
                row["mse1"] = mse1
                row["mse2"] = mse2 
                row["error"] = "FAILED TO RUN" 
                print(row["msid"], mse1, mse2, "FAILED TO RUN")
                print("siena_optibet", t1_file1, t1_file2, "-o",\
                  "/data/henry11/PBR_long/subjects/" + os.path.split(msid)[-1].split(".txt")[0]+ '/' + mse1 + '_to_' + mse2)
                t1_new = os.path.split(t1_file1)[0] + glob("*T1mni.nii.gz*")
       
                print(t1_new, "T1 NEW") 
                cmd = ["siena_optibet", t1_file1, t1_file2, "-o",\
                  "/data/henry11/PBR_long/subjects/" + os.path.split(msid)[-1].split(".txt")[0] + '/' + mse1 + '_to_' + mse2]
                proc = Popen(cmd)
                proc.wait()
            else: 
                row["mse1"] = mse1
                row["mse2"] = mse2 
                row["error"] = "N/A"
 
                





        #spreadsheet.writerow(row)

writer.close()


"""

    if os.path.exists(base_dir + mse + "/sienax_flair/"):
        path = base_dir + mse + "/nii/"
        first_file = next(os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)))
        msid = os.path.split(first_file)[1].split("-")[0]
        print(msid)
        
        
        row = {"msid": msid, "Scan Status": "Skyra", "mseID": mse}
        check_call(["ms_dcm_echo", "-p", password])
        output = check_output(["ms_get_phi", "--examID", mse, "--studyDate", "-p", password])
        output = [output.decode('utf8')]
        for line in output:
            if "StudyDate" in line:
                row["Scan Date"] = line.split()[-1]

        report = os.path.join(base_dir, mse, "sienax_flair/report.sienax")
        with open(report, "r") as f:
            lines = [line.strip() for line in f.readlines()]
            for line in lines:
                if not len(line) >= 1:
                    continue
                if line.startswith("VSCALING"):
                    row["vscale"] = line.split()[1]
                elif line.startswith("pgrey"):
                    row["cortical vol (u, mm3)"] = line.split()[2]
                elif line.startswith("vcsf"):
                    row["vCSF vol (u, mm3)"] = line.split()[2]
                elif line.startswith("GREY"):
                    row["GM vol (u, mm3)"] = line.split()[2]
                elif line.startswith("WHITE"):
                    row["WM vol (u, mm3)"] = line.split()[2]
                elif line.startswith("BRAIN"):
                    row["brain vol (u, mm3)"] = line.split()[2]
""" 


