import csv
import os
import pbr
from pbr.base import _get_output
import pandas as pd
import argparse
import json
import numpy as np
import nibabel as nib
from subprocess import check_output, check_call
from getpass import getpass


password = getpass("mspacman password: ")
check_call(["ms_dcm_echo", "-p", password])

def get_align(mse):
    align = _get_output(mse)+"/"+mse+"/alignment/status.json"
    return align


def run_siena_sienax(c,sienax,  out):
    writer = open("{}".format(out), "w")
    spreadsheet = csv.DictWriter(writer, fieldnames=["msid", "mseID",
                                                    "siena", "PBVC","T1_1", "T1_2", "vscale",
                                                    "brain vol (u, mm3)",
                                                    "WM vol (u, mm3)",
                                                    "GM vol (u, mm3)",
                                                    "vCSF vol (u, mm3)",
                                                    "cortical vol (u, mm3)",
                                                    "lesion vol (u, mm3)",
                                                    "Scan Date", "PatientSex", "BirthDate", "scanner"
                                                      ])

    spreadsheet.writeheader()

    df = pd.read_csv("{}".format(c))

    for _, row in df.iterrows():
        msid = "ms" + str(row['msid']).lstrip("0")
        mse =  str(row["mse"])
        print(msid, mse)
        row = {"msid": msid, "mseID": mse}

        #getting siena data

        siena_long = "/data/henry10/PBR_long/subjects/" + msid + '/siena_optibet/'

        if os.path.exists(siena_long):
            for mse_siena in os.listdir(siena_long):
                if mse_siena.startswith(mse):
                    row["siena"] = mse_siena
                    mse1 =  "mse" + mse_siena.split("mse")[1].split("_")[0]
                    mse2 = "mse" + mse_siena.split("mse")[2]
                    siena_report = os.path.join(siena_long, mse_siena, "report.siena")

                    if not os.path.exists(siena_report):
                        continue
                    with open(siena_report, "r") as f:
                        lines = [line.strip() for line in f.readlines()]
                        for line in lines:
                            if line.startswith("finalPBVC"):
                                row["PBVC"] =  line.split()[1]
                    if os.path.exists(get_align(mse2)):
                        with open(get_align(mse2)) as data_file:
                            data = json.load(data_file)
                        if len(data["t1_files"]) == 0:
                            continue
                        else:
                            t1_file2 = data["t1_files"][-1].split('/')[-1]
                            row["T1_2"] = t1_file2

        if os.path.exists(get_align(mse)):

            with open(get_align(mse)) as data_file:
                data = json.load(data_file)
            if len(data["t1_files"]) == 0:
                continue
            else:
                t1_file = data["t1_files"][-1].split('/')[-1]
                row["T1_1"] = t1_file


        #getting sienax data
        base_dir = _get_output(mse) + '/' + mse + '/' + sienax
        if os.path.exists(base_dir):
            print(base_dir)
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

            check_call(["ms_dcm_echo", "-p", password])
            output = check_output(["ms_get_phi", "--examID", mse, "--studyDate", "-p", password])
            output = [output.decode('utf8')]
            for line in output:
                if "StudyDate" in line:
                    row["Scan Date"] = line.split()[-1]
                if "PatientSex" in line:
                    row["PatientSex"] = line.split()[-1]
                if "PatientBirthDate" in line:
                    row["BirthDate"] = line.split()[-1]
                if "StationName" in line:
                    row["scanner"] = line.split()[-1]

        spreadsheet.writerow(row)

    writer.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code allows you to grab siena values given a csv (with mse and msid) and an output csv')
    parser.add_argument('-i', help = 'csv containing the msid and mse')
    parser.add_argument('-s', help = 'PBR directory name i.e., sienax_flair ')
    parser.add_argument('-o', help = 'output csv for siena data')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    sienax = args.s
    out = args.o
    print(c, out)
    run_siena_sienax(c,sienax, out)



