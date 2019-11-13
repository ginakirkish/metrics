import os
import pandas as pd
import argparse
import json
import numpy as np
import nibabel as nib
from glob import glob
from subprocess import Popen, PIPE
from getpass import getpass

def _get_output(mse):
    mse_num = int(mse[3:])
    if mse_num <= 4500:
        output_dir = '/data/henry7/PBR/subjects'
    else:
        output_dir = '/data/henry11/PBR/subjects'
    return output_dir

password = getpass("mspacman password: ")

df = pd.read_csv("/home/sf522915/Documents/EPIC1_sienax_siena_first_COMBINED_DEC10_new.csv")
df.columns.values[1:62]

for idx in range(len(df)):
    mse = df.loc[idx, 'mse']
    df.loc[idx,"mse1"] = mse
    print(mse)
    msid = df.loc[idx, 'msid']
    msid = "ms" + msid.replace("ms","").lstrip("0")
    if os.path.exists(_get_output(mse)+"/"+mse+"/nii/status.json"):
        with open(_get_output(mse)+"/"+mse+"/nii/status.json") as data_file:
            data = json.load(data_file)
            if len(data["t1_files"]) > 0:
                t1_file = data["t1_files"][-1].split('/')[-1].split("-")[3].split(".nii.gz")[0]
                df.loc[idx, "T1"] = t1_file
                print("T1 file ===============", t1_file)
            if len(data["t2_files"]) > 0:
                t2_file = data["t2_files"][-1].split('/')[-1].split("-")[3].split(".nii.gz")[0]
                df.loc[idx, "T2"] = t2_file
                print("T2 file ===============", t2_file)
            if len(data["flair_files"]) > 0:
                flair_file = data["flair_files"][-1].split('/')[-1].split("-")[3].split(".nii.gz")[0]
                df.loc[idx, "FLAIR"] = flair_file
                print("FLAIR ==========", flair_file)

    try:

        cmd = ["ms_get_phi", "--examID", mse, "-p", password]
        proc = Popen(cmd, stdout=PIPE)
        output = str([l.decode("utf-8").split() for l in proc.stdout.readlines()[:]])

        birth = output.split("PatientBirthDate")[1].split("=")[1].split("StudyTime")[0].replace("'","").replace(",","").replace("[","").replace("]","")
        #print(birth)
        df.loc[idx, "BirthDate"] = birth

        scan_date = output.split("StudyDate")[1].split("=")[1].replace("'","").replace(",","").replace("[","").replace("]","")
        #print("scan date", scan_date)
        df.loc[idx, "ScanDate - mse1"] = scan_date

        dicom = glob("/working/henry_temp/PBR/dicoms/{0}/E*/*/*.DCM".format(mse))[0]
        cmd = ["dcmdump", dicom]
        proc = Popen(cmd, stdout=PIPE)
        output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
        x = ["SoftwareVersions", "BodyPartExamined", "StationName"]
        for line in output:
            for flag in x:
                if flag in line:
                    dicom_info = str(str(line[2:]).split(']')[0].split('[')[2:]).replace('[',"").replace(']','').replace('"','').replace("'","")
                    #print(flag,":", dicom_info)
                    if flag == "SoftwareVersions":
                        df.loc[idx,"SoftwareVersions - mse1"] = dicom_info
                    if flag == "StationName":
                        df.loc[idx,"StationName - mse1"] = dicom_info



    except:
        pass

    timepoint = df.loc[idx, 'VisitType']
    sienax_bl = ""
    siena_long = "/data/henry10/PBR_long/subjects/" + str(msid) + "/siena_optibet/"
    siena_path = str(df.loc[idx, 'siena_path'])
    print(siena_path)

    pbvc = df.loc[idx, 'PBVC']
    if os.path.exists(siena_long):
        for mse_siena in os.listdir(siena_long):
            if mse_siena.startswith(mse):
                df.loc[idx,"siena_path"] = mse_siena
                mse2 = "mse" + mse_siena.split("mse")[2].replace("_","")
                df.loc[idx, "mse2"] = mse2
                siena_report = os.path.join(siena_long, mse_siena, "report.siena")

                if not os.path.exists(siena_report):
                    continue
                with open(siena_report, "r") as f:
                    lines = [line.strip() for line in f.readlines()]
                    for line in lines:
                        if line.startswith("finalPBVC"):
                            df.loc[idx, 'PBVC'] =  line.split()[1]
                if os.path.exists(_get_output(mse2)+"/"+mse2+"/nii/status.json"):
                    with open(_get_output(mse2)+"/"+mse2+"/nii/status.json") as data_file:
                        data = json.load(data_file)
                        if len(data["t1_files"]) > 0:
                            t1_filemse2 = data["t1_files"][-1].split('/')[-1].split("-")[3].split(".nii.gz")[0]
                            df.loc[idx, "T1 - mse2"] = t1_filemse2
                try:

                    cmd = ["ms_get_phi", "--examID", mse2, "-p", password]
                    proc = Popen(cmd, stdout=PIPE)
                    output = str([l.decode("utf-8").split() for l in proc.stdout.readlines()[:]])

                    scan_date = output.split("StudyDate")[1].split("=")[1].replace("'","").replace(",","").replace("[","").replace("]","")
                    #print("scan date", scan_date)
                    df.loc[idx, "ScanDate - mse2"] = scan_date

                    dicom = glob("/working/henry_temp/PBR/dicoms/{0}/E*/*/*.DCM".format(mse2))[0]
                    cmd = ["dcmdump", dicom]
                    proc = Popen(cmd, stdout=PIPE)
                    output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
                    x = ["SoftwareVersions", "BodyPartExamined", "StationName"]
                    for line in output:
                        for flag in x:
                            if flag in line:
                                dicom_info = str(str(line[2:]).split(']')[0].split('[')[2:]).replace('[',"").replace(']','').replace('"','').replace("'","")
                                #print(flag,":", dicom_info)
                                if flag == "SoftwareVersions":
                                    df.loc[idx,"SoftwareVersions - mse2"] = dicom_info
                                if flag == "StationName":
                                    df.loc[idx,"StationName - mse2"] = dicom_info


                except:
                    pass

    """if os.path.exists(_get_output(mse) +"/"+ mse + "/first/"):
        print(_get_output(mse) +"/"+ mse + "/first/")
        for files in os.listdir(_get_output(mse) + "/" +mse +"/first/"):
            if files.endswith("firstseg.nii.gz"):

                print(files)
                seg = _get_output(mse) + "/" +mse +"/first/"+ files

                cmd = ["fslstats",seg,"-l", "9.5", "-u","10.5", "-V"]
                proc = Popen(cmd, stdout=PIPE)
                lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0]
                df.loc[idx,"L Thalamus"] = lines

                cmd = ["fslstats",seg,"-l", "10.5", "-u","11.5", "-V"]
                proc = Popen(cmd, stdout=PIPE)
                lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0]
                df.loc[idx,"L Caudate"] = lines

                cmd = ["fslstats",seg,"-l", "11.5", "-u","12.5", "-V"]
                proc = Popen(cmd, stdout=PIPE)
                lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0]
                df.loc[idx,"L Putamen"] = lines

                cmd = ["fslstats",seg,"-l", "48.5", "-u","49.5", "-V"]
                proc = Popen(cmd, stdout=PIPE)
                lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0]
                df.loc[idx,"R Thalamus"] = lines

                cmd = ["fslstats",seg,"-l", "49.5", "-u","50.5", "-V"]
                proc = Popen(cmd, stdout=PIPE)
                lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0]
                df.loc[idx,"R Caudate"] = lines

                cmd = ["fslstats",seg,"-l", "50.5", "-u","51.5", "-V"]
                proc = Popen(cmd, stdout=PIPE)
                lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0]
                df.loc[idx,"R Putamen"] = lines"""


    sienax_flair = str(_get_output(mse) + '/' + mse + '/sienaxorig_flair/')
    sienax_t2 =  str(_get_output(mse) + '/' + mse + '/sienaxorig_t2/')
    sienax_noles = str(_get_output(mse) +'/' +mse +'/sienaxorig_noles/')
    if os.path.exists(sienax_flair):
        sienax = sienax_flair
        df.loc[idx, "SIENAX"] = "sienaxorig_flair"
    elif os.path.exists(sienax_t2):
        sienax = sienax_t2
        df.loc[idx, "SIENAX"] = "sienaxorig_t2"
    elif os.path.exists(sienax_noles):
        sienax = sienax_noles
        df.loc[idx, "SIENAX"] = "sienaxorig_noles"
    else:
        sienax = ""
    print(sienax)
    if len(sienax) > 1:
        #df.loc[idx, "SIENAX"] = sienax.split("/")[6]
        print("SIENAX =================",sienax.split("/")[6] )

        report = sienax + '/report.sienax'
        with open(report, "r") as f:
                lines = [line.strip() for line in f.readlines()]
                for line in lines:
                    if not len(line) >= 1:
                        continue
                    if line.startswith("VSCALING"):
                        df.loc[idx, "vscale origT1"] = line.split()[1]
                        print(mse,"vscale new origT1",line.split()[1])
                    elif line.startswith("pgrey"):
                        df.loc[idx,"cortical vol (u, mm3) origT1"] =line.split()[2]
                    elif line.startswith("vcsf"):
                        df.loc[idx,"vCSF vol (u, mm3) origT1"] = line.split()[2]
                    elif line.startswith("GREY"):
                        df.loc[idx,"GM vol (u, mm3) origT1"] = line.split()[2]
                    elif line.startswith("WHITE"):
                        df.loc[idx,"WM vol (u, mm3) origT1"] = line.split()[2]
                    elif line.startswith("BRAIN"):
                        df.loc[idx,"brain vol (u, mm3) origT1"] = line.split()[2]



        lm = sienax +  "/lesion_mask.nii.gz"
        if os.path.exists(lm):
            img = nib.load(lm)
            data = img.get_data()
            df.loc[idx, "lesion vol (u, mm3) origT1"] = np.sum(data)
            print(mse, np.sum(data), "LESION NEW")



    df.to_csv("/home/sf522915/Documents/EPIC1_sienax_siena_first_COMBINED_DEC12_3.csv")


