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
import pbr
from pbr.base import _get_output 

df = pd.read_csv("/home/sf522915/sienax_data_reginacontrol.csv")


writer = open("/home/sf522915/csv/first_data_control.csv", "w")
spreadsheet = csv.DictWriter(writer, 
                             fieldnames=["msid", "mse", 
                                        "L Thalamus",
                                        "R Thalamus", 
                                        "L Caudate",
                                        "R Caudate", 
                                        "L Putamen",
                                        "R Putamen",
                                        "ExamDate", 
                                        "Age_calculated_RS",
                                        "vscale", 
                                        "brain vol (u, mm3)",
                                        "WM vol (u, mm3)", 
                                        "GM vol (u, mm3)",
                                        "vCSF vol (u, mm3)",
                                        "cortical vol (u, mm3)",
                                        "lesion vol (u, mm3)", "mseID", "flair file"])
spreadsheet.writeheader()


for _, row in df.iterrows():
    mse = row['mseID']
    msid = row['msid']
    ExamDate = row['date']
    row = {"msid": msid, "mse": mse, "ExamDate": ExamDate}
    if len(mse) >= 7:
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

                      
    spreadsheet.writerow(row)

writer.close()

