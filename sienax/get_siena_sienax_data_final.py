import csv
import os
import pbr
from pbr.base import _get_output
import pandas as pd
import argparse
import json
import numpy as np
import nibabel as nib


def get_align(mse):
    mse = str(mse)
    align = _get_output(mse)+"/"+mse+"/alignment/status.json"
    return align



def extract_dicom(line, x):
    if x in line:
        print(x,":", dicom_info)
        row = {x: dicom_info}



def run_siena_sienax(c,sienax,  out):
    writer = open("{}".format(out), "w")
    print(writer)
    spreadsheet = csv.DictWriter(writer, fieldnames=["msid", "mseID","errors", "visit", "date", "scanner", "SoftwareVersions", \
                                                    "BodyPartExamined", "StationName", "ReceiveCoilName", "TransmitCoilName",
                                                    "siena", "PBVC","T1_1", "T1_2","T1_file", "T2_file", "FLAIR_file", "vscale",
                                                    "brain vol (u, mm3)",
                                                    "WM vol (u, mm3)",
                                                    "GM vol (u, mm3)",
                                                    "vCSF vol (u, mm3)",
                                                    "cortical vol (u, mm3)",
                                                    "lesion vol (u, mm3)"
                                                      ])
    spreadsheet.writeheader()

    df = pd.read_csv("{}".format(c))

    for _, row in df.iterrows():
        msid = str(row['msid'])
        mse =  row["mse"]
        mse = str(mse)
        print(msid, mse)
        #errors = str(row["errors"])
        #visit = str(row["VisitType"])
        date =str(row["date"])
        #scanner = str(row["scanner"])
        coil = ""
        software = ""
        body = ""


        print(msid, mse)
        row = {"msid": msid, "mseID": mse, "date": date} #,"scanner": scanner}




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
            print(get_align(mse))
            with open(get_align(mse)) as data_file:
                data = json.load(data_file)
            if len(data["t1_files"]) == 0:
                continue
            else:
                t1_file = data["t1_files"][-1].split('/')[-1]
                row["T1_1"] = t1_file
        #getting sienax data
        base_dir = _get_output(mse) + '/' + mse + '/' + sienax
        print(base_dir)
        if os.path.exists(base_dir + "/lesion_mask.nii.gz"):


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
            print(np.sum(data))

        if os.path.exists(get_align(mse)):
                with open(get_align(mse)) as data_file:
                    data = json.load(data_file)
                    if len(data["t1_files"]) == 0:
                        row["T1_file"] = ""
                    else:

                        t1_file = data["t1_files"][-1].split('/')[-1]
                        row["T1_file"] = t1_file

                    if len(data["t2_files"]) == 0:
                        row["T2_file"] = ""
                    else:
                        t2_file = data["t2_files"][-1].split('/')[-1]
                        row["T2_file"] = t2_file

                    if len(data["flair_files"]) == 0:
                        row["FLAIR_file"] = ""
                    else:
                        flair_file = data["flair_files"][-1].split('/')[-1]
                        row["FLAIR_file"] = flair_file







        dicom = ""
        try:
            dicom = glob("/working/henry_temp/PBR/dicoms/{0}/E*/*/*.DCM".format(mse))[0]
        except:
            pass
        if len(dicom) > 1:
            print("***************************")
            print(mse)
            cmd = ["dcmdump", dicom]
            proc = Popen(cmd, stdout=PIPE)
            output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
            for line in output:


                extract_dicom(line,"SoftwareVersions")
                extract_dicom(line,"BodyPartExamined")
                extract_dicom(line,"StationName")
                extract_dicom(line,"ReceiveCoilName")
                extract_dicom(line,"Coil")
                extract_dicom(line,"TransmitCoilName")



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



