
import nibabel as nib
import numpy as np
import csv
import os
import pbr
from pbr.base import _get_output
import pandas as pd
import argparse





def run_sienax(c, sienax, out):


    writer = open("{}".format(out), "w")

    spreadsheet = csv.DictWriter(writer,
                             fieldnames=["msid", "mseID",
                                        "vscale",
                                        "brain vol (u, mm3)",
                                        "WM vol (u, mm3)",
                                        "GM vol (u, mm3)",
                                        "vCSF vol (u, mm3)",
                                        "cortical vol (u, mm3)",
                                        "lesion vol (u, mm3)"])
    spreadsheet.writeheader()

    df = pd.read_csv("{}".format(c))
    for _, row in df.iterrows():
        msid = str(row["msid"])
        mse = str(row["mse"])
        base_dir = ""
        print(msid, mse)
        if mse.startswith("mse"):
            base_dir = _get_output(mse) + '/' + mse + '/' + sienax
            print(msid, mse)

        if os.path.exists(base_dir):
            print(base_dir)
            row = {"msid": msid, "mseID": mse}


            report = base_dir + "/report.sienax"
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

            lm = base_dir +  "/lesion_mask.nii.gz"
            img = nib.load(lm)
            data = img.get_data()
            row["lesion vol (u, mm3)"] = np.sum(data)

            spreadsheet.writerow(row)

    writer.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code allows you to grab sienax values given a csv (with mse and msid) and the PBR sienax directory name and an output csv filename')
    parser.add_argument('-i', help = 'csv containing the msid and mse')
    parser.add_argument('-s', help = 'PBR directory name i.e., sienax_flair ')
    parser.add_argument('-o', help = 'output csv for sienax data')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    sienax = args.s
    out = args.o
    print(c, sienax, out)
    run_sienax(c, sienax, out)



