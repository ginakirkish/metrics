from glob import glob
import pandas as pd
import numpy as np
import csv
import os
from subprocess import Popen, PIPE
from pbr.base import _get_output
import json
import nibabel as nib
import argparse





#df = pd.read_csv("/home/sf522915/Documents/siena_antje_transistion.csv")
#df = pd.read_csv("/home/sf522915/Documents/carlo_siena.csv")
df = pd.read_csv("/home/sf522915/Documents/EPIC1_sienax_clincalPASAT_merged_Oct17.csv")

def write_spreadsheet(df):

    writer = open("/home/sf522915/Documents/EPIC_siena.csv", "w")
    spreadsheet = csv.DictWriter(writer, fieldnames=["msID", "mseID","examdate",
                                                     "siena", "PBVC","sienax_flair", "sienax_t2","sienax", "T1", "T2", "FLAIR", \
                                                     "vscale",
                                                     "brain vol (u, mm3)",
                                                     "WM vol (u, mm3)",
                                                     "GM vol (u, mm3)",
                                                     "vCSF vol (u, mm3)",
                                                     "cortical vol (u, mm3)",
                                                     "lesion vol (u, mm3)" ])
    spreadsheet.writeheader()


    for _, row in df.iterrows():
        msid ="ms"+ str(row['msid']).replace("ms", "").lstrip("0")
        #msid = "ms" + msid.replace("ms", "").lstrip("0")

        siena_long = "/data/henry11/PBR_long/subjects/" + msid
        #date = row["examdate"]
        date = ""
        mse =  str(row["mse"])

        print(msid, mse)

        sienax_flair = ""
        sienax_t2 = ""
        sienax = ""
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
        pbvc = ""
        FINALmse_siena = ""




        if mse.startswith("mse"):

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




            elif os.path.exists(_get_output(mse) + "/" + mse + "/sienax_t2"):
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


                    lm = os.path.join(_get_output(mse), mse, "sienax_t2/lesion_mask.nii.gz")
                    img = nib.load(lm)
                    data = img.get_data()
                    lesion = np.sum(data)

            elif os.path.exists(_get_output(mse) + "/" + mse + "/sienax"):
                sienax = "sienax no lesion mask"
                list = os.listdir(_get_output(mse)+ '/' + mse + "/sienax/") # dir is your directory path
                report = glob(os.path.join(_get_output(mse), mse, "sienax/*/report.sienax"))[0]
                print(report)
                print("# #######################################################################")

                if os.path.exists(report):
                    print(report, "THIS IS THE SIENAX WITHOUT LESION MASKS")
                    with open(report, "r") as f:
                        lines = [line.strip() for line in f.readlines()]
                        for line in lines:
                            if line.startswith("VSCALING"):
                                vscale =  line.split()[1]
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



            if os.path.exists(_get_output(mse)+"/"+mse+"/alignment/status.json"):


                with open(_get_output(mse)+"/"+mse+"/alignment/status.json") as data_file:
                    data = json.load(data_file)
                    if len(data["t1_files"]) == 0:
                        continue
                    else:
                        t1_file = data["t1_files"][-1]
                        t1_file = (t1_file.split('/')[-1])
                        #mseID = t1_file.split("-")[1]
                        series = t1_file.split("-")[2].lstrip("0")
                        if not len(series) > 0:
                            series = "1"
                        try:
                            dcm = glob("/working/henry_temp/PBR/dicoms/{0}/E*/{1}/*.DCM".format(mse,series))
                        except:
                            pass
                        if len(dcm) > 0 :
                            dcm = dcm[0]
                            cmd = ["dcmdump", dcm]
                            proc = Popen(cmd, stdout=PIPE)

                            lines = str([l.decode("utf-8").split() for l in proc.stdout.readlines()[:]])
                            row["scanner"] = lines
                            if "qb3-3t" in lines:
                                scanner = "qb3"
                            elif "SIEMENS" in lines:
                                scanner = "Skyra"
                            elif "CB3TMR"  or "CB-3TMR" in lines:
                                scanner = "CB"
                            else:
                                scanner = "unknown"



                    if len(data["t2_files"]) == 0:
                        row = {"T2": "NONE"}
                    else:
                        t2_file = data["t2_files"][-1]
                        t2_file = (t2_file.split('/')[-1])
                        row = {"T2": t2_file}
                    if len(data["flair_files"]) == 0:
                        row = {"FLAIR": "NONE"}
                    else:
                        flair_file = data["flair_files"][-1]
                        flair_file = (flair_file.split('/')[-1])
                        row = {"FLAIR": flair_file}


            if os.path.exists(siena_long):
                for mse_siena in os.listdir(siena_long):
                    if mse_siena.startswith(mse):
                        FINALmse_siena = mse_siena
                        print(siena_long + '/' + FINALmse_siena, "THIS IS THE SIENA LONG DIRECTORY")
                        siena_report = os.path.join(siena_long, FINALmse_siena, "report.siena")
                        print(siena_report, "THIS IS THE SIENA REPORT")
                        if not os.path.exists(siena_report):
                            continue
                        with open(siena_report, "r") as f:
                            lines = [line.strip() for line in f.readlines()]
                            for line in lines:
                                if line.startswith("finalPBVC"):
                                    pbvc =  line.split()[1]
                                    row = {"PBVC": pbvc}
                                    print(pbvc, "THIS IS THE PBVC")
                                    row = {"siena" : FINALmse_siena}
                                    print(mse_siena, "THIS IS THE MSE SIENA #####")



        row = {"msID": msid, "mseID": mse,"examdate": date,
                "sienax_flair" : sienax_flair, "sienax_t2": sienax_t2, "sienax": sienax , "T1": t1_file, "T2": t2_file, "FLAIR": flair_file, \
                "vscale": vscale,
                "brain vol (u, mm3)": brain,
                "WM vol (u, mm3)" : wm,
                "GM vol (u, mm3)": gm,
                "vCSF vol (u, mm3)": csf,
                "cortical vol (u, mm3)": cortical,
                "lesion vol (u, mm3)": lesion, "PBVC": pbvc, "siena": FINALmse_siena}


        print(row)
        spreadsheet.writerow(row)
    writer.close()

write_spreadsheet(df)

