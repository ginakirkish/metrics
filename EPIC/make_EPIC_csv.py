

import argparse
import pbr
import os
from glob import glob
from pbr.base import _get_output
from subprocess import Popen, PIPE
from getpass import getpass
import json
from nipype.utils.filemanip import load_json
heuristic = load_json(os.path.join(os.path.split(pbr.__file__)[0], "heuristic.json"))["filetype_mapper"]
from pbr.workflows.nifti_conversion.utils import description_renamer
import pandas as pd
import shutil
import nibabel as nib
import numpy as np
import csv


def get_mse(msid):
    mse = date = tmp = ""
    cmd = ["ms_get_patient_imaging_exams", "--patient_id", msid, "--dcm_dates"]
    proc = Popen(cmd, stdout=PIPE)
    lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[5:]]
    tmp = pd.DataFrame(lines, columns=["mse", "date"])
    tmp["msid"] = msid
    return tmp

def get_modality(mse, sequence):
    num = mse.split("mse")[-1]
    cmd = ["ms_dcm_exam_info", "-t", num]
    proc = Popen(cmd, stdout=PIPE)
    lines = [description_renamer(" ".join(l.decode("utf-8").split()[1:-1])) for l in proc.stdout.readlines()[8:]]
    sequence_name = ""
    nii_type = sequence
    if nii_type:
        try:
            sequence_name = filter_files(lines, nii_type, heuristic)[0]
            print(sequence_name, "This is the {0}".format(sequence))
        except:
            pass
        return sequence_name

def filter_files(descrip,nii_type, heuristic):
    output = []
    for i, desc in enumerate(descrip):
        if desc in list(heuristic.keys()):
            if heuristic[desc] == nii_type:
                 output.append(desc)
    return output

def get_scanner_info(mse, x):
    info = ""
    try:
        dicom = glob("/working/henry_temp/PBR/dicoms/{0}/E*/*/*.DCM".format(mse))[0]
        cmd = ["dcmdump", dicom]
        proc = Popen(cmd, stdout=PIPE)
        output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
        for line in output:
            if x in line:
                dicom_info = str(str(line[2:]).split(']')[0].split('[')[2:]).replace('[',"").replace(']','').replace('"','').replace("'","")
                info = dicom_info
    except:
        pass
    return info

def get_first_values(mse):
    L_thal=L_caud=L_put=L_pall=L_hipp= L_amy= L_acc=  R_thal= R_caud= R_put=R_pall= R_hipp= R_amy= R_acc=BS = ''
    status = "{}/{}/first_all/status.json".format(_get_output(mse),mse)
    if os.path.exists(status):
        with open(status, "r") as f:
            lines = [line.strip() for line in f.readlines()]
            for line in lines:
                if "Brain-Stem" in line:
                    print(line)
                    BS = line.split()[3].replace(",","")
                    print(BS, "^^^^^^^^^^^^^^^^^^")
                elif "Left-Accumbens"in line:
                    L_acc = line.split()[1].replace(",","")
                elif "Left-Amy"in line:
                    L_amy = line.split()[1].replace(",","")
                elif "Left-Caud"in line:
                    L_caud = line.split()[1].replace(",","")
                elif "Left-Hipp"in line:
                    L_hipp = line.split()[1].replace(",","")
                elif "Left-Palli"in line:
                    L_pall = line.split()[1].replace(",","")
                elif "Left-Puta"in line:
                    L_put = line.split()[1].replace(",","")
                elif "Left-Thalamus"in line:
                    L_thal = line.split()[1].replace(",","")
                elif "Right-Accumbens"in line:
                    R_acc = line.split()[1].replace(",","")
                elif "Right-Amy"in line:
                    R_amy = line.split()[1].replace(",","")
                elif "Right-Caud"in line:
                    R_caud = line.split()[1].replace(",","")
                elif "Right-Hipp"in line:
                    R_hipp = line.split()[1].replace(",","")
                elif "Right-Palli"in line:
                    R_pall = line.split()[1].replace(",","")
                elif "Right-Puta"in line:
                    R_put = line.split()[1].replace(",","")
                elif "Right-Thalamus"in line:
                    R_thal = line.split()[1].replace(",","")

                else:
                    continue
    print(L_thal,L_caud,L_put,L_pall,L_hipp, L_amy, L_acc,  R_thal, R_caud, R_put,R_pall, R_hipp, R_amy, R_acc,BS)
    return [L_thal,L_caud,L_put,L_pall,L_hipp, L_amy, L_acc,  R_thal, R_caud, R_put,R_pall, R_hipp, R_amy, R_acc,BS]


def get_sienax_values(sienax, sienax_label):
    VS=PG=VCSF= GM= WM= BV= les_vol = ""
    if os.path.exists(sienax):
        with open(sienax, "r") as f:
            lines = [line.strip() for line in f.readlines()]
            for line in lines:
                if not len(line) >= 1:
                    continue

                if line.startswith("VSCALING"):
                    try:
                        VS = line.split()[1]
                    except:
                        VS = ""
                        pass
                elif line.startswith("pgrey"):
                    PG = line.split()[2]
                elif line.startswith("vcsf"):
                    VCSF = line.split()[2]
                elif line.startswith("GREY"):
                    GM = line.split()[2]
                elif line.startswith("WHITE"):
                    WM = line.split()[2]
                elif line.startswith("BRAIN"):
                    BV = line.split()[2]
        lm = sienax.replace("report.sienax","") +  "/lesion_mask.nii.gz"

        if os.path.exists(lm):
            img = nib.load(lm)
            data = img.get_data()
            les_vol = np.sum(data)
    return [sienax_label, VS, PG, VCSF, GM, WM, BV, les_vol]


def get_sienax_path(mse):
    sienax_label =sienax = VS= PG= VCSF= GM= WM= BV = les_vol= ""
    sienax_optibet = glob("/{0}/{1}/sienax_optibet/ms*/report.sienax".format(_get_output(mse),mse))
    sienax_fl = "/{0}/{1}/sienaxorig_flair/report.sienax".format(_get_output(mse),mse)
    sienax_t2 = "/{0}/{1}/sienaxorig_t2/report.sienax".format(_get_output(mse),mse)
    if len(sienax_optibet) >= 1:
        print(sienax_optibet)
        sienax = sienax_optibet[0].replace("lesion_mask.nii.gz", "report.sienax")
        if os.path.exists("/{0}/{1}/lesion_origspace_flair/".format(_get_output(mse),mse)):
            sienax_label = "sienaxorig_flair"
        else:
            sienax_label = "sienaxorig_t2"
    elif os.path.exists(sienax_fl):
        sienax_label = "sienaxorig_flair"
        sienax = sienax_fl
    elif os.path.exists(sienax_t2):
        sienax_label = "sienaxorig_t2"
        sienax = sienax_t2
    elif os.path.exists(sienax_fl.replace("sienaxorig","sienax")):
        sienax_label = "sienax_flair"
        sienax = sienax_fl.replace("sienaxorig","sienax") + "/report.html"
    elif os.path.exists(sienax_t2.replace("sienaxorig","sienax")):
        sienax_label = "sienax_t2"
        sienax = sienax_t2.replace("sienaxorig","sienax") + "/report.html"
    elif os.path.exists(sienax_t2.replace("sienaxorig", "sienax_optibet")):
        sienax_label = "sienax_optibet"
        sienax = sienax_t2.replace("sienaxorig", "sienax_optibet") + "/report.html"
    else:
        sienax = ""
        sienax_label = ""
    SX = get_sienax_values(sienax, sienax_label)
    return SX






def write_csv(c, out):
    msid = mse = date = " "
    df = pd.read_csv("{}".format(c))
    writer = open("{}".format(out), "w")
    spreadsheet = csv.DictWriter(writer, fieldnames=["msid", "mse", "date","tag", "T1", "T2", "FLAIR", "Software", "Scanner", \
                                                    'Left-Thalamus-Proper',
                                                    'Left-Caudate',
                                                    'Left-Putamen',
                                                    'Left-Pallidum',
                                                    'Left-Hippocampus',
                                                    'Left-Amygdala',
                                                    'Left-Accumbens',
                                                    'Right-Thalamus-Proper',
                                                    'Right-Caudate',
                                                    'Right-Putamen',
                                                    'Right-Pallidum',
                                                    'Right-Hippocampus',
                                                    'Right-Amygdala',
                                                    'Right-Accumbens',
                                                    'Brain Stem', "sienax",
                                                     'V Scale', "pGM", "CSF", "GM", "WM", "BV", "Lesion"
                                                    ])
    spreadsheet.writeheader()

    for idx in range(len(df)):
        msid = str(df.loc[idx, 'msid'])
        epic_study = df.loc[idx, "EPIC"]
        print(msid, epic_study)
        value = get_mse(msid)
        for _, row in value.iterrows():
            mse = "mse" + str(row["mse"])
            date = row["date"]
            print(msid, mse, date)
            F = get_first_values(mse)
            SX = get_sienax_path(mse)
            #siena = get_siena_data(msid, mse1, mse2)
            #df.loc[idx, "pbvc"] = Siena[0]

            row = {"msid": "ms"+msid,
                   "mse": mse,
                   "date":date,
                   "tag": epic_study,
                   "T1": get_modality(mse, "T1"),
                   "T2": get_modality(mse, "T2"),
                   "FLAIR":  get_modality(mse, "FLAIR"),
                   "Software": get_scanner_info(mse, "SoftwareVersions"),
                   "Scanner": get_scanner_info(mse, "StationName"),
                    'Left-Thalamus-Proper': F[0], 'Left-Caudate':F[1],'Left-Putamen':F[2],'Left-Pallidum':F[3],'Left-Hippocampus':F[4],'Left-Amygdala':F[5],
                    'Left-Accumbens':F[6], 'Right-Thalamus-Proper':F[7],'Right-Caudate':F[8],'Right-Putamen':F[9], 'Right-Pallidum':F[10], 'Right-Hippocampus':F[11],
                   'Right-Amygdala':F[12],'Right-Accumbens':F[13],'Brain Stem':F[14],
                   'sienax': SX[0],'V Scale': SX[1],'pGM': SX[2],'CSF': SX[3],'GM': SX[4],'WM': SX[5],"BV": SX[6],"Lesion": SX[7]

                   }
            spreadsheet.writerow(row)
    writer.close()
    #tmp.to_csv("{}".format(out))




if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code allows you to grab the mse, scanner, birthdate, sex  given a csv (with date and msid)')
    parser.add_argument('-i', help = 'csv containing the msid and date')
    parser.add_argument('-o', help = 'output csv for siena data')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    out = args.o
    print(c, out)
    write_csv(c, out)