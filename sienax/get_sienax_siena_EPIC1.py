import csv
import os
import pbr
from pbr.base import _get_output
import pandas as pd
import argparse
import json
import numpy as np
import nibabel as nib
from glob import glob
from subprocess import Popen, PIPE

def get_align(mse):
    align = _get_output(str(mse))+"/"+str(mse)+"/alignment/status.json"
    return align







def run_siena_sienax(c, out):
    writer = open("{}".format(out), "w")
    print(writer)
    spreadsheet = csv.DictWriter(writer, fieldnames=["msid", "mseID","EPIC_Project", "errors", "visit", "date", "scanner","SoftwareVersions", "Coefficient",\
                                                    "BodyPartExamined", "StationName", "ReceiveCoilName", "TransmitCoilName",
                                                    "siena", "PBVC","T1_1", "T1_2","T1_file", "T2_file", "FLAIR_file","sienax", "vscale",\
                                                    "cal brain", "cal wm", "cal gm",  "cal cort", "cal csf","cal les",
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
        mse =  str(row["mse"])
        mse = str(mse)
        print(msid, mse)
        errors = str(row["errors"])
        visit = str(row["VisitType"])
        date =str(row["Brain_MRI_Date"])
        scanner = str(row["scanner"])
        proj = str(row["EPIC_Project"])
        coef = str(row["Coefficient"])
        brain = str(row["nBV"])
        wm = str(row["nWM"])
        gm = str(row["nGM"])
        csf = str(row["nCSF"])
        cort = str(row["nCorticalVolume"])
        les = str(row["nLV"])
        software = ""
        body = ""
        station = ""
        rcoil = ""
        tcoil = ""

        print(msid, mse)
        row = {"msid": msid, "mseID": mse, "errors":errors, "visit": visit, "date": date,"scanner": scanner, "Coefficient": coef}


        if coef == "CBO":
            print(float(brain))
            row["cal brain"] = float(brain) * float(1.002283085)
            row["cal wm"] = float(wm) * float(1.041687205)
            row["cal gm"] = float(gm) * (0.968717012)
            row["cal cort"] = float(cort) * 1.002283085
            row["cal csf"] = float(csf) *1.331222384
            row["cal les"] = float(les) * 2.27593177

        if coef == "CBO2":
            row["cal brain"] = float(brain) *0.990150288
            row["cal wm"] = float(wm) *0.965869282
            row["cal gm"] = float(gm) *0.965869282
            row["cal cort"] = float(cort) *0.996528008
            row["cal csf"] = float(csf) *1.300728069
            row["cal les"] = float(les) *2.553610789

        if coef == "CBU":
            row["cal brain"] = float(brain) *0.949602208
            row["cal wm"] = float(wm) *0.999107691
            row["cal gm"] = float(gm) *2.01186027
            row["cal cort"] = float(cort) *0.93229982
            row["cal csf"] = float(csf) *2.01186027
            row["cal les"] = float(les) *6.300453627

        if coef == "CBU2":
            row["cal brain"] = float(brain) *1.002210984
            row["cal wm"] = float(wm) *1.046212716
            row["cal gm"] = float(gm) *0.965040357
            row["cal cort"] = float(cort) *0.994677622
            row["cal csf"] = float(csf) *1.528234702
            row["cal les"] = float(les) *3.666652029

        if coef == "CBUF":
            row["cal brain"] = float(brain) *0.988888879
            row["cal wm"] = float(wm) *1.03897916
            row["cal gm"] = float(gm) *0.946764313
            row["cal cort"] = float(cort) *0.9811215
            row["cal csf"] = float(csf) *1.466142502
            row["cal les"] = float(les) *2.433227636

        if coef == "CBUF2":
            row["cal brain"] = float(brain) *0.969845769
            row["cal wm"] = float(wm) *1.020961734
            row["cal gm"] = float(gm) *0.927248682
            row["cal cort"] = float(cort) *0.949473556
            row["cal csf"] = float(csf) *1.49038892
            row["cal les"] = float(les) *4.267844427


        if coef == "QB3":
            row["cal brain"] = float(brain) *0.983283939
            row["cal wm"] = float(wm) *0.975925407
            row["cal gm"] = float(gm) *0.990458979
            row["cal cort"] = float(cort) *0.989010586
            row["cal csf"] = float(csf) * 1.436252775
            row["cal les"] = float(les) *1.334164109

        if coef == "QB32":
            row["cal brain"] = float(brain) * 0.980519454
            row["cal wm"] = float(wm) * 0.976436448
            row["cal gm"] = float(gm) * 0.984680158
            row["cal cort"] = float(cort) *0.981813999
            row["cal csf"] = float(csf) * 1.364435355
            row["cal les"] = float(les) * 2.922327291

        if coef == "Skyra":
            row["cal brain"] = float(brain) * 1
            row["cal wm"] = float(wm) * 1
            row["cal gm"] = float(gm) * 1
            row["cal cort"] = float(cort) *1
            row["cal csf"] = float(csf) * 1
            row["cal les"] = float(les) * 1
            print("Skyra")


        """


        #gina's coefficients
        if coef == "CBO":
            print(float(brain))
            row["cal brain"] = float(brain) * 1.003388766
            row["cal wm"] = float(wm) * 1.101756028
            row["cal gm"] = float(gm) * 0.91942734
            row["cal cort"] = float(cort) * 0.966402971
            row["cal csf"] = float(csf) *1.073332857
            row["cal les"] = float(les) *2.617060502

        if coef == "CBO2":
            print(float(brain))
            row["cal brain"] = float(brain) * 0.986066073
            row["cal wm"] = float(wm) * 1.097278005
            row["cal gm"] = float(gm) * 0.891697589
            row["cal cort"] = float(cort) * 0.934974415
            row["cal csf"] = float(csf) *1.027439265
            row["cal les"] = float(les) *3.200969125

        if coef == "CBU":
            print(float(brain))
            row["cal brain"] = float(brain) * 0.95087793
            row["cal wm"] = float(wm) * 1.055807324
            row["cal gm"] = float(gm) * 0.863345108
            row["cal cort"] = float(cort) * 0.896019432
            row["cal csf"] = float(csf) *1.624204982
            row["cal les"] = float(les) *7.230890024

        if coef == "CBU2":
            print(float(brain))
            row["cal brain"] = float(brain) * 1.002675712
            row["cal wm"] = float(wm) * 1.109001014
            row["cal gm"] = float(gm) * 0.912857013
            row["cal cort"] = float(cort) * 0.952316691
            row["cal csf"] = float(csf) *1.228677516
            row["cal les"] = float(les) *4.30048893

        if coef == "CBUF":
            print(float(brain))
            row["cal brain"] = float(brain) * 0.991151146
            row["cal wm"] = float(wm) * 1.094409028
            row["cal gm"] = float(gm) * 0.904235529
            row["cal cort"] = float(cort) * 0.946883342
            row["cal csf"] = float(csf) *1.186251458
            row["cal les"] = float(les) *2.78909433


        if coef == "CBUF2":
            print(float(brain))
            row["cal brain"] = float(brain) * 0.972080121
            row["cal wm"] = float(wm) * 1.075309336
            row["cal gm"] = float(gm) * 0.902145925
            row["cal cort"] = float(cort) * 0.916356892
            row["cal csf"] = float(csf) *1.206908764
            row["cal les"] = float(les) *4.878400658

        if coef == "QB3":
            print(float(brain))
            row["cal brain"] = float(brain) * 0.990120611
            row["cal wm"] = float(wm) * 1.011687459
            row["cal gm"] = float(gm) * 0.969592773
            row["cal cort"] = float(cort) * 0.944342424
            row["cal csf"] = float(csf) *1.179130696
            row["cal les"] = float(les) *1.422149934

        if coef == "QB32":
            print(float(brain))
            row["cal brain"] = float(brain) * 0.98737836
            row["cal wm"] = float(wm) * 1.012006601
            row["cal gm"] = float(gm) * 0.964060167
            row["cal cort"] = float(cort) * 0.967388815
            row["cal csf"] = float(csf) *1.119659125
            row["cal les"] = float(les) *3.165227429

        if coef == "Skyra1":
            print(float(brain))
            row["cal brain"] = float(brain) * 0.983177779
            row["cal wm"] = float(wm) * 1.016851156
            row["cal gm"] = float(gm) * 0.951937613
            row["cal cort"] = float(cort) *0.963534136
            row["cal csf"] = float(csf) *1.180407566
            row["cal les"] = float(les) *1.850396275
            print("Skyra1", les)

        if coef == "Skyra2":
            print(float(brain))
            row["cal brain"] = float(brain) * 0.989221413
            row["cal wm"] = float(wm) * 0.99691049
            row["cal gm"] = float(gm) * 0.981764912
            row["cal cort"] = float(cort) * 0.983113645
            row["cal csf"] = float(csf) *1.019325265
            row["cal les"] = float(les) *1.238185214
            print("Skyra2", les)


        if coef == "Skyra3":
            print(float(brain))
            row["cal brain"] = float(brain) * 1
            row["cal wm"] = float(wm) * 1
            row["cal gm"] = float(gm) * 1
            row["cal cort"] = float(cort) * 1
            row["cal csf"] = float(csf) * 1
            row["cal les"] = float(les) * 1
            print("SKYRA3")
            """




        dicom = ""
        try:
            dicom = glob("/working/henry_temp/PBR/dicoms/{0}/E*/*/*.DCM".format(mse))[0]
        except:
            pass
        if len(dicom) > 1:
            print("***************************")
            print(mse)
            try:
                cmd = ["dcmdump", dicom]
                proc = Popen(cmd, stdout=PIPE)
                output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
                """for line in output:
                    if "SoftwareVersions" in line:
                        software = str(str(line[2:]).split(']')[0].split('[')[2:]).replace('[',"").replace(']','').replace('"','').replace("'","")
                    if "BodyPartExamined" in line:
                        body = str(str(line[2:]).split(']')[0].split('[')[2:]).replace('[',"").replace(']','').replace('"','').replace("'","")"""

                x = ["SoftwareVersions", "BodyPartExamined", "StationName", "TransmitCoilName", "ReceiveCoilName"]
                for line in output:
                    for flag in x:
                        if flag in line:

                            dicom_info = str(str(line[2:]).split(']')[0].split('[')[2:]).replace('[',"").replace(']','').replace('"','').replace("'","")
                            print(flag,":", dicom_info)

                            if flag == "SoftwareVersions":
                                row["SoftwareVersions"] = dicom_info
                                #row = {"SoftwareVersions": dicom_info}
                            if flag == "BodyPartExamined":
                                row["BodyPartExamined"] = dicom_info
                                #row = {"BodyPartExamined": dicom_info}
                            if flag == "StationName":
                                row["StationName"] = dicom_info
                                #row = {"StationName": dicom_info}
                            if flag == "TransmitCoilName":
                                row["TransmitCoilName"] = dicom_info
                                #row = {"TransmitCoilName": dicom_info}
                            if flag == "ReceiveCoilName":
                                row["ReceiveCoilName"] = dicom_info
                                #row = {"ReceiveCoilName": dicom_info}
            except:
                pass







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

        s = ["sienax_t2", "sienax_flair"]
        for sienax in s:
            print(sienax)
            base_dir = _get_output(str(mse)) + '/' + str(mse) + '/' + sienax
            print(base_dir)
            if os.path.exists(base_dir + '/lesion_mask.nii.gz'):
                row["sienax"] = sienax


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







        spreadsheet.writerow(row)

    writer.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code allows you to grab siena values given a csv (with mse and msid) and an output csv')
    parser.add_argument('-i', help = 'csv containing the msid and mse')
    parser.add_argument('-o', help = 'output csv for siena data')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    out = args.o
    print(c, out)
    run_siena_sienax(c,out)



"""
        if coef == "CBO1":
            print(float(brain) * float(1.0310978262))
            row["cal brain"] = float(brain) * float(1.0310978262)
            row["cal wm"] = float(wm) * float(1.0608498714)
            row["cal gm"] = float(gm) * 1.0035627217
            row["cal cort"] = float(cort) * 1.0390221217
            row["cal csf"] = float(csf) *  0.9222879789
            row["cal les"] = float(les) * 1.2144000716

        if coef == "CBO":
            row["cal brain"] = float(brain) * float(1.0394662152)
            row["cal wm"] = float(wm) * 1.0608498714
            row["cal gm"] = float(gm) * 1.0035627217
            row["cal cort"] = float(cort) * 1.0390221217
            row["cal csf"] = float(csf) * 0.9222879789
            row["cal les"] = float(les) * 1.2144000716

        if coef == "CBU":
            row["cal brain"] = float(brain) * 1.0388704291
            row["cal wm"] = float(wm) * 1.0742640328
            row["cal gm"] = float(gm) * 1.0067663478
            row["cal cort"] = float(cort) * 1.0447576591
            row["cal csf"] = float(csf) * 0.9967509037
            row["cal les"] = float(les) * 1.0256638502

        if coef == "CBUF":
            row["cal brain"] = float(brain) * 1.0253992641
            row["cal wm"] = float(wm) * 1.068831218
            row["cal gm"] = float(gm) * 0.9869873626
            row["cal cort"] = float(cort) * 1.0229975619
            row["cal csf"] = float(csf) * 1.0003134073
            row["cal les"] = float(les) * 1.0095082188

        if coef == "QB3":
            row["cal brain"] = float(brain) * 1.00421939
            row["cal wm"] = float(wm) * 0.9891698259
            row["cal gm"] = float(gm) * 1.0163033437
            row["cal cort"] = float(cort) * 1.0158779206
            row["cal csf"] = float(csf) * 1.0105091699
            row["cal les"] = float(les) * 1.0328504986

        if coef == "Skyra":
            row["cal brain"] = float(brain) * 1
            row["cal wm"] = float(wm) * 1
            row["cal gm"] = float(gm) * 1
            row["cal cort"] = float(cort) *1
            row["cal csf"] = float(csf) * 1
            row["cal les"] = float(les) * 1


        #gina's coefficients
        if coef == "CBO":
            print(float(brain))
            row["cal brain"] = float(brain) * float(1.002283085)
            row["cal wm"] = float(wm) * float(1.041687205)
            row["cal gm"] = float(gm) * (0.968717012)
            row["cal cort"] = float(cort) * 1.002283085
            row["cal csf"] = float(csf) *1.331222384
            row["cal les"] = float(les) * 2.27593177

        if coef == "CBO2":
            row["cal brain"] = float(brain) *0.990150288
            row["cal wm"] = float(wm) *0.965869282
            row["cal gm"] = float(gm) *0.965869282
            row["cal cort"] = float(cort) *0.996528008
            row["cal csf"] = float(csf) *1.300728069
            row["cal les"] = float(les) *2.553610789

        if coef == "CBU":
            row["cal brain"] = float(brain) *0.949602208
            row["cal wm"] = float(wm) *0.999107691
            row["cal gm"] = float(gm) *2.01186027
            row["cal cort"] = float(cort) *0.93229982
            row["cal csf"] = float(csf) *2.01186027
            row["cal les"] = float(les) *6.300453627

        if coef == "CBU2":
            row["cal brain"] = float(brain) *1.002210984
            row["cal wm"] = float(wm) *1.046212716
            row["cal gm"] = float(gm) *0.965040357
            row["cal cort"] = float(cort) *0.994677622
            row["cal csf"] = float(csf) *1.528234702
            row["cal les"] = float(les) *3.666652029

        if coef == "CBUF":
            row["cal brain"] = float(brain) *0.988888879
            row["cal wm"] = float(wm) *1.03897916
            row["cal gm"] = float(gm) *0.946764313
            row["cal cort"] = float(cort) *0.9811215
            row["cal csf"] = float(csf) *1.466142502
            row["cal les"] = float(les) *2.433227636

        if coef == "CBUF2":
            row["cal brain"] = float(brain) *0.969845769
            row["cal wm"] = float(wm) *1.020961734
            row["cal gm"] = float(gm) *0.927248682
            row["cal cort"] = float(cort) *0.949473556
            row["cal csf"] = float(csf) *1.49038892
            row["cal les"] = float(les) *4.267844427


        if coef == "QB3":
            row["cal brain"] = float(brain) *0.983283939
            row["cal wm"] = float(wm) *0.975925407
            row["cal gm"] = float(gm) *0.990458979
            row["cal cort"] = float(cort) *0.989010586
            row["cal csf"] = float(csf) * 1.436252775
            row["cal les"] = float(les) *1.334164109

        if coef == "QB32":
            row["cal brain"] = float(brain) * 0.980519454
            row["cal wm"] = float(wm) * 0.976436448
            row["cal gm"] = float(gm) * 0.984680158
            row["cal cort"] = float(cort) *0.981813999
            row["cal csf"] = float(csf) * 1.364435355
            row["cal les"] = float(les) * 2.922327291

        if coef == "Skyra":
            row["cal brain"] = float(brain) * 1
            row["cal wm"] = float(wm) * 1
            row["cal gm"] = float(gm) * 1
            row["cal cort"] = float(cort) *1
            row["cal csf"] = float(csf) * 1
            row["cal les"] = float(les) * 1






"""