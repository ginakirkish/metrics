from subprocess import check_output, check_call
from getpass import getpass
#import nibabel as nib
import numpy as np
from glob import glob
import csv
import os
from subprocess import Popen, Popen, PIPE
import pandas as pd
import nibabel as nib

#df = pd.read_csv("/home/sf522915/check_process_roland.csv")
df = pd.read_csv("/home/sf522915/Documents/carlo_first.csv")
def _get_output(mse):
    mse_num = int(mse[3:]) 
    if mse_num <= 4500:
        output_dir = '/data/henry7/PBR/subjects'
    else:
        output_dir = '/data/henry11/PBR/subjects'
    return output_dir

writer = open("/home/sf522915/Documents/first_carlo.csv", "w")
spreadsheet = csv.DictWriter(writer, 
                             fieldnames=["msid", "mse", 
                                        "L Thalamus",
                                        "R Thalamus", 
                                        "L Caudate",
                                        "R Caudate", 
                                        "L Putamen",
                                        "R Putamen",
                                        "ExamDate", 
                                        "vscale", 
                                        "brain vol (u, mm3)",
                                        "WM vol (u, mm3)", 
                                        "GM vol (u, mm3)",
                                        "vCSF vol (u, mm3)",
                                        "cortical vol (u, mm3)",
                                        "lesion vol (u, mm3)", "mseID", "flair file"])
spreadsheet.writeheader()


for _, row in df.iterrows():
    mse = str(row['mse'])
    msid = row['msid']
    #ExamDate = row['error']
    #Age_calculated = row["Age"]
    row = {"msid": msid, "mse": mse}
    #if len(mse) >= 7:
    print(mse, msid)
    if os.path.exists(_get_output(mse) +"/"+ mse + "/first/"):
        print(_get_output(mse) +"/"+ mse + "/first/")
        for files in os.listdir(_get_output(mse) + "/" +mse +"/first/"):
            if files.endswith("firstseg.nii.gz"):
                print(files)
                seg = _get_output(mse) + "/" +mse +"/first/"+ files
                    
                cmd = ["fslstats",seg,"-l", "9.5", "-u","10.5", "-V"]
                proc = Popen(cmd, stdout=PIPE)
                lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0]
                row["L Thalamus"] = lines
                    
                cmd = ["fslstats",seg,"-l", "10.5", "-u","11.5", "-V"]
                proc = Popen(cmd, stdout=PIPE)
                lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0]
                row["L Caudate"] = lines
                    
                cmd = ["fslstats",seg,"-l", "11.5", "-u","12.5", "-V"]
                proc = Popen(cmd, stdout=PIPE)
                lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0]
                row["L Putamen"] = lines
                   
                cmd = ["fslstats",seg,"-l", "48.5", "-u","49.5", "-V"]
                proc = Popen(cmd, stdout=PIPE)
                lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0]
                row["R Thalamus"] = lines
                    
                cmd = ["fslstats",seg,"-l", "49.5", "-u","50.5", "-V"]
                proc = Popen(cmd, stdout=PIPE)
                lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0]
                row["R Caudate"] = lines
                
                cmd = ["fslstats",seg,"-l", "50.5", "-u","51.5", "-V"]
                proc = Popen(cmd, stdout=PIPE)
                lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0]
                row["R Putamen"] = lines

    if os.path.exists(_get_output(mse)+ "/"+ mse + "/sienaxorig_flair/report.sienax"):                   
        report = os.path.join(_get_output(mse)+ "/"+ mse + "/sienaxorig_flair/report.sienax")
        with open(report, "r") as f:
            lines = [line.strip() for line in f.readlines()]
            for line in lines:    
                if line.startswith("VSCALING"):
                    row["vscale"] =  line.split()[1]
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

        lm = os.path.join(_get_output(mse), mse, "sienaxorig_flair/lesion_mask.nii.gz")
        img = nib.load(lm)
        data = img.get_data()
        row["lesion vol (u, mm3)"] = np.sum(data)
    elif os.path.exists(_get_output(mse)+ "/"+ mse + "/sienaxorig_t2/report.sienax"):                   
        report = os.path.join(_get_output(mse)+ "/"+ mse + "/sienaxorig_t2/report.sienax")
        with open(report, "r") as f:
            lines = [line.strip() for line in f.readlines()]
            for line in lines:    
                if line.startswith("VSCALING"):
                    row["vscale"] =  line.split()[1]
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

    elif os.path.exists(_get_output(mse)+ "/"+ mse + "/sienaxorig_noles/report.sienax"):                   
        report = os.path.join(_get_output(mse)+ "/"+ mse + "/sienaxorig_noles/report.sienax")
        with open(report, "r") as f:
            lines = [line.strip() for line in f.readlines()]
            for line in lines:    
                if line.startswith("VSCALING"):
                    row["vscale"] =  line.split()[1]
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
    elif os.path.exists(_get_output(mse)+ "/"+ mse + "/sienax_optibet/report.sienax"):                   
        report = os.path.join(_get_output(mse)+ "/"+ mse + "/sienax_optibet/report.sienax")
        with open(report, "r") as f:
            lines = [line.strip() for line in f.readlines()]
            for line in lines:    
                if line.startswith("VSCALING"):
                    row["vscale"] =  line.split()[1]
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

    else:
        print("no sienax")

                
                
                    
                    
                    
                    
    spreadsheet.writerow(row)

writer.close()
