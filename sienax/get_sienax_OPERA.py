import nibabel as nib
import numpy as np
from glob import glob
import csv
import os
import pbr
from pbr.base import _get_output
import pandas as pd
from subprocess import Popen

writer = open("/home/sf522915/sienax_data_pbr.csv", "w")
spreadsheet = csv.DictWriter(writer,
                             fieldnames=["msid",
                                        "vscale",
                                        "brain vol (u, mm3)",
                                        "WM vol (u, mm3)",
                                        "GM vol (u, mm3)",
                                        "vCSF vol (u, mm3)",
                                        "cortical vol (u, mm3)",
                                        "lesion vol (u, mm3)", "mseID"])
spreadsheet.writeheader()

df = pd.read_csv("/home/sf522915/Documents/OPERA_sienax.csv")


for _, row in df.iterrows():

    msid = str(row["msid"])
    mse = str(row['mseid'])
    print(msid, mse)
    sienax = _get_output(mse) + '/' + mse + '/sienax_t1manseg/'
    print(sienax)

    if os.path.exists(sienax):
        row = {}
        row["msid"] = msid
        row["mseID"] = mse


        report = _get_output(mse) +'/'+ mse +"/sienax_t1manseg/report.sienax"
        print(report)
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

        lm = _get_output(mse) + '/' + mse + "/sienax_t1manseg/lesion_mask.nii.gz"
        print(lm)
        img = nib.load(lm)
        data = img.get_data()
        row["lesion vol (u, mm3)"] = np.sum(data)

        cmd = ["fslmaths",  _get_output(mse) + '/' + mse + "/sienax_t1manseg/I_stdmaskbrain_pve_2.nii.gz","-bin", \
               "-sub", _get_output(mse) + '/' + mse + "/sienax_t1manseg/lesion_mask.nii.gz", "-bin",  _get_output(mse) + '/' + mse + "/sienax_t1manseg/wm_mask.nii.gz"]
        Popen(cmd).wait()
        print(cmd)



        spreadsheet.writerow(row)

writer.close()