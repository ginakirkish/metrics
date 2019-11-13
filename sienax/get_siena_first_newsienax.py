
import pandas as pd
import argparse
import json
import numpy as np
import nibabel as nib
from glob import glob
from subprocess import Popen, PIPE
from getpass import getpass

password = getpass("mspacman password: ")

#df = pd.read_csv("/home/sf522915/Documents/Excluded.csv")
#df = pd.read_csv("/home/sf522915/Documents/EPIC1_sienax_clincalPASAT_merged_Oct17new.csv")
#df = pd.read_csv("/home/sf522915/Documents/Gina_EPIC1_sienax_first.csv")
#df = pd.read_csv("/home/sf522915/Documents/ALL_EPIC_COMBINED.csv")
#df = pd.read_csv("/home/sf522915/Documents/EPIC1_sienax_siena_first_withSIENAprotocol_Dates_Nov30.csv")
df = pd.read_csv("/home/sf522915/Documents/EPIC1_sienax_siena_first_withSIENAprotocolandDatesDEC6.csv")
df.columns.values[1:62]

for idx in range(len(df)):


    mse = df.loc[idx, 'mse']
    print(mse)
    brain = df.loc[idx, 'nBV']
    msid = df.loc[idx, 'Sienax msid']
    timepoint = df.loc[idx, 'VisitType']
    #if "Baseline" in timepoint:
    sienax_bl = ""
    siena_long = "/data/henry10/PBR_long/subjects/" + str(msid) + "/siena_optibet/"
    siena_path = str(df.loc[idx, 'siena_path'])
    print(siena_path)
    mse2 = str(df.loc[idx, 'mse2'])
    """try:
        cmd = ["ms_get_phi", "--examID", mse2, "-p", password]
        #print(cmd)
        proc = Popen(cmd, stdout=PIPE)
        output = str([l.decode("utf-8").split() for l in proc.stdout.readlines()[:]])

        scan_date = output.split("StudyDate")[1].split("=")[1].replace("'","").replace(",","").replace("[","").replace("]","")
        print("scan date", scan_date)
        df.loc[idx, "ScanDate - Second TP"] = scan_date
    except:
        pass"""

    try:
        dicom = glob("/working/henry_temp/PBR/dicoms/{0}/E*/*/*.DCM".format(mse2))[0]
        cmd = ["dcmdump", dicom]
        proc = Popen(cmd, stdout=PIPE)
        output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
        x = ["SoftwareVersions", "BodyPartExamined", "StationName", "TransmitCoilName", "ReceiveCoilName"]
        for line in output:
            for flag in x:
                if flag in line:

                    dicom_info = str(str(line[2:]).split(']')[0].split('[')[2:]).replace('[',"").replace(']','').replace('"','').replace("'","")
                    print(flag,":", dicom_info)

                    if flag == "SoftwareVersions":
                        df.loc[idx,"SoftwareVersions - mse2"] = dicom_info
                    if flag == "StationName":
                        df.loc[idx,"StationName - mse2"] = dicom_info
                    if flag == "TransmitCoilName":
                        df.loc[idx,"TransmitCoilName - mse2"] = dicom_info
                    if flag == "ReceiveCoilName":
                        df.loc[idx,"ReceiveCoilName - mse2"] = dicom_info

    except:
        df.loc[idx, "dicom"] = "no dicom in working directory"
        pass

    """
    if "mse" in siena_path:

        mse1 = "mse" +siena_path.split("mse")[1].replace("_","")
        mse2 = "mse" + siena_path.split("mse")[2].replace("_","")


        try:
            dicom1 = glob("/working/henry_temp/PBR/dicoms/{0}/E*/*/*.DCM".format(mse1))[0]
            cmd = ["dcmdump", dicom1]
            proc = Popen(cmd, stdout=PIPE)
            output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
            for line in output:
                if "StationName" in line:
                    dicom_info1 = str(str(line[2:]).split(']')[0].split('[')[2:]).replace('[',"").replace(']','').replace('"','').replace("'","")
                    print(mse1, dicom_info1)
                    df.loc[idx,"SIENA - FIRST TP Scanner"] = dicom_info1

            dicom2 = glob("/working/henry_temp/PBR/dicoms/{0}/E*/*/*.DCM".format(mse2))[0]
            cmd = ["dcmdump", dicom2]
            proc = Popen(cmd, stdout=PIPE)
            output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
            for line in output:
                if "StationName" in line:
                    dicom_info2 = str(str(line[2:]).split(']')[0].split('[')[2:]).replace('[',"").replace(']','').replace('"','').replace("'","")
                    print(mse2, dicom_info2)
                    df.loc[idx,"SIENA - SECOND TP Scanner"] = dicom_info2

            cmd = ["ms_get_phi", "--examID", mse2, "-p", password]
            #print(cmd)
            proc = Popen(cmd, stdout=PIPE)
            output = str([l.decode("utf-8").split() for l in proc.stdout.readlines()[:]])

            birth = output.split("PatientBirthDate")[1].split("=")[1].split("StudyTime")[0].replace("'","").replace(",","").replace("[","").replace("]","")
            print(birth)
            df.loc[idx, "BirthDate - Second TP"] = birth

            scan_date = output.split("StudyDate")[1].split("=")[1].replace("'","").replace(",","").replace("[","").replace("]","")
            print("scan date", scan_date)
            df.loc[idx, "ScanDate - Second TP"] = scan_date


        except:
            pass




    pbvc = df.loc[idx, 'PBVC']
    if str(pbvc) == float(0):
        if os.path.exists(siena_long):
            for mse_siena in os.listdir(siena_long):
                if mse_siena.startswith(mse):
                    df.loc[idx,"siena_path"] = mse_siena
                    mse1 =  "mse" + mse_siena.split("mse")[1].split("_")[0]
                    mse2 = "mse" + mse_siena.split("mse")[2]
                    siena_report = os.path.join(siena_long, mse_siena, "report.siena")

                    if not os.path.exists(siena_report):
                            continue
                    with open(siena_report, "r") as f:
                        lines = [line.strip() for line in f.readlines()]
                        for line in lines:
                            if line.startswith("finalPBVC"):
                                df.loc[idx, 'PBVC'] =  line.split()[1]

    thalamus = df.loc[idx,'L Thalamus']
    if str(thalamus) == "0":
        print(int(thalamus), "THALAMUS", 0)
        if os.path.exists(_get_output(mse) +"/"+ mse + "/first/"):
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
                    df.loc[idx,"R Putamen"] = lines


    try:
        sienax_bl = glob(str(_get_output(mse) + '/' + mse + '/sienaxorig_*/'))[0]
        if os.path.exists(sienax_bl):
            report = sienax_bl + '/report.sienax'
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
        lm = sienax_bl +  "/lesion_mask.nii.gz"
        if os.path.exists(lm):
            img = nib.load(lm)
            data = img.get_data()
            df.loc[idx, "lesion vol (u, mm3) origT1"] = np.sum(data)
            print(mse, np.sum(data), "LESION NEW")


    except:
        pass"""


    df.to_csv("/home/sf522915/Documents/EPIC1_sienax_siena_first_withSIENA_DEC6.csv")
    #df.to_csv("/home/sf522915/Documents/EPIC1_sienax_siena_first_clinical_withSIENAprotocol.csv")
    #df.to_csv("/home/sf522915/Documents/EPIC1_sienax_dataCOMBINED.csv")
