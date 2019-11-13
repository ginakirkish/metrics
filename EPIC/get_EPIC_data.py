
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

password = getpass("mspacman password: ")

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

def get_dicom(mse):
    dicom = "/working/henry_temp/PBR/dicom/{}/E*".format(mse)
    if len(dicom) > 0:
        dicom = "True"
    else:
        dicom = "False"
    return dicom

def get_nifti(mse):
    nifti = _get_output(mse)+"/"+mse+"/nii/status.json"
    if not os.path.exists(nifti):
        nii = "False"
    else:
        nii = "True"
    return nii

def get_align(mse):
    align = _get_output(mse)+"/"+mse+"/alignment/status.json"
    if not os.path.exists(align):
        align = "False"
    else:
        align = "True"
    return align

def get_first(mse):
    try:
        first = glob("/{0}/{1}/first_all/*fast_firstseg*".format(_get_output(mse), mse))[0]
        first = "True"
    except:
        first = "False"
        pass
    return first

def calc_first(seg, num):
    num1 = num - .5
    num2 = num + .5
    cmd = ["fslstats",seg,"-l", "{}".format(num1), "-u","{}".format(num2), "-V"]
    proc = Popen(cmd, stdout=PIPE)
    area = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0]
    return(area)


def get_first_values_old(mse):
    L_thal,L_caud,L_put,L_pall,L_hipp, L_amy, L_acc,  R_thal, R_caud, R_put,R_pall, R_hipp, R_amy, R_acc,BS = '','','','','','','','','','','','','','',''
    if os.path.exists(_get_output(mse) +"/"+ mse + "/first_all/"):
        for files in os.listdir(_get_output(mse) + "/" +mse +"/first_all/"):
            if files.endswith("firstseg.nii.gz") or files.endswith("firstsegs.nii.gz"):
                print(files)
                seg = _get_output(mse) + "/" +mse +"/first_all/"+ files
                L_thal = calc_first(seg, 10)
                L_caud = calc_first(seg, 11)
                L_put = calc_first(seg, 12)
                L_pall = calc_first(seg, 13)
                L_hipp = calc_first(seg, 17)
                L_amy = calc_first(seg, 18)
                L_acc = calc_first(seg,26)
                R_thal = calc_first(seg, 49)
                R_caud = calc_first(seg, 50)
                R_put = calc_first(seg, 51)
                R_pall = calc_first(seg, 52)
                R_hipp = calc_first(seg, 53)
                R_amy = calc_first(seg, 54)
                R_acc = calc_first(seg,58)
                BS = calc_first(seg, 16)

    return [L_thal,L_caud,L_put,L_pall,L_hipp, L_amy, L_acc,  R_thal, R_caud, R_put,R_pall, R_hipp, R_amy, R_acc,BS]

def get_first_values(mse):
    L_thal,L_caud,L_put,L_pall,L_hipp, L_amy, L_acc,  R_thal, R_caud, R_put,R_pall, R_hipp, R_amy, R_acc,BS = '','','','','','','','','','','','','','',''
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



def get_brainstem(mse):
    BS = ""
    bs = glob("{}/{}/first_brainstem/*firstseg*".format(_get_output(mse), mse))
    if len(bs) > 0: 
        bs = bs[0]
        BS = calc_first(bs, 16)
    return BS


def get_FS(msid,mse):
    try:
        fs = glob("/data/henry6/PBR/surfaces/*{0}*{1}*".format(msid,mse))[0]
        print(fs)
        fs = "True"
    except:
        fs = "False"
        pass
    return fs

def get_sienax(mse):
    les_vol = ""
    sienax_label, sienax, VS, PG, VCSF, GM, WM, BV = "", "", "", "", "", "", "", ""
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
        """try:
            sienax = glob("/{0}/{1}/sienax*/ms*/report.sienax".format(_get_output(mse),mse))[-1]
        except:
            sienax_label = "False"
            pass"""
    if os.path.exists(sienax):
        with open(sienax, "r") as f:
            lines = [line.strip() for line in f.readlines()]
            for line in lines:
                if not len(line) >= 1:
                    continue
                if line.startswith("VSCALING"):
                    VS = line.split()[1]
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



def get_siena_data(msid, mse, mse2):
    #siena_long = glob("/data/henry*/PBR_long/subjects/" + msid + '/siena_optibet/')
    henry12 = "/data/henry12/PBR_long/subjects/" + msid + '/siena_optibet/'
    henry10 = "/data/henry10/PBR_long/subjects/" + msid + '/siena_optibet/'
    pbvc_henry12, mse2_t1, siena_label, pbvc_henry10, final_pbvc = "", "", "", "",""
    try:
        align = "{}/{}/alignment/status.json".format(_get_output(mse2), mse2)
        if os.path.exists(align):
            with open(align) as data_file:
                data = json.load(data_file)
                if len(data["t1_files"]) > 0:
                    mse2_t1 = data["t1_files"][-1].split('/')[-1].split('-')[3].replace(".nii.gz", "")
                    if "DESPOT" in mse2_t1:
                        mse2_t1 = data["t1_files"][0]
                    print("MSE2", mse2_t1)
    except:
        pass
    if os.path.exists(henry12):
        for mse_siena12 in os.listdir(henry12):
            if str(mse_siena12).startswith(str(mse)) and str(mse_siena12).endswith(str(mse2)):
                siena_report = os.path.join(henry12, mse_siena12, "report.siena")
                if os.path.exists(siena_report):
                    print(siena_report)
                    siena_label = "True"
                    with open(siena_report, "r") as f:
                        lines = [line.strip() for line in f.readlines()]
                        for line in lines:
                            if line.startswith("finalPBVC"):
                                pbvc_henry12 =  line.split()[1]


    if os.path.exists(henry10):
        for mse_siena in os.listdir(henry10):
            if str(mse_siena).startswith(str(mse)) and str(mse_siena).endswith(str(mse2)):
                siena_report = os.path.join(henry10, mse_siena, "report.siena")
                if os.path.exists(siena_report):
                    print(siena_report)
                    siena_label = "True"
                    with open(siena_report, "r") as f:
                        lines = [line.strip() for line in f.readlines()]
                        for line in lines:
                            if line.startswith("finalPBVC"):
                                pbvc_henry10 =  line.split()[1]
                                siena_path = henry10 + mse_siena

    if len(pbvc_henry10) >4 and len(pbvc_henry12) > 4:
        if pbvc_henry10 > pbvc_henry12:
            final_pbvc = pbvc_henry12
            print(mse,mse2)
            print( pbvc_henry10, "this is larger than...",  pbvc_henry12)
            print("removing.....", siena_path)
            shutil.rmtree(siena_path)
        else:
            final_pbvc = pbvc_henry10
    elif len(pbvc_henry12) > 4:
        final_pbvc = pbvc_henry12
    elif len(pbvc_henry10) > 4:
        final_pbvc = pbvc_henry10
    else:
        final_pbvc = ""

    return [final_pbvc, mse2_t1, siena_label]

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

def sienax_long(msid, mse):
    pbr_long = "/data/henry10/PBR_long/subjects/"
    if not os.path.exists(pbr_long + msid + "/lst_edit_sienax/"):
        lst_long = False
    else:
        lst_long = True
    return lst_long

def get_lst(mse):
    lst = ""
    try:
        lst = glob(_get_output(mse)+"/"+mse+"/mindcontrol/ms*/lst/lst_edits/no_FP_filled_*")[0]
    except:
        pass
    if len(lst) > 3:
        lst = "LST - FINISHED"
    elif os.path.exists(_get_output(mse)+"/"+mse+ "/lst/lpa"):
        lst = "lst - not edited"
    else:
        lst = "none"
    return lst

def check_for_resampling_sienax(mse):
    check = ""
    try:
        t1 = glob("{}/{}/sienaxorig_*/I_brain.nii.gz".format(_get_output(mse), mse ))[-1]
        cmd = ["fslstats", t1, "-R" ]
        proc = Popen(cmd, stdout=PIPE)
        max = str(float([l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][-1]))
        check = ""
        if max.endswith(".0"):
            check = True
        else:
            check = False
    except:
        pass
    return check


def check_for_resampling_align(mse):
        check = ""
        align = _get_output(mse)+"/"+mse+"/alignment/status.json"
        if os.path.exists(align):
            with open(align) as data_file:
                data = json.load(data_file)
                if len(data["t1_files"]) > 0:
                    t1_file = data["t1_files"][-1]
                    try:
                        cmd = ["fslstats", t1_file, "-R" ]
                        proc = Popen(cmd, stdout=PIPE)
                        max = str(float([l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][-1]))
                        check = ""
                        if max.endswith(".0"):
                            check = True
                        else:
                            check = False
                    except:
                        pass
                    return check

def check_for_resampling_siena(msid, mse):
    check = True
    siena_check = "/data/henry6/gina/siena_check/"
    pbr = ["/data/henry10/PBR_long/subjects", "/data/henry12/PBR_long/subjects"]
    for pbr_long in pbr:
        siena = glob("{}/{}/siena_optibet/{}_*".format(pbr_long, msid, mse))
        if len(siena) > 0:
            print(siena)
            siena = siena[0]
            for items in siena:
                A_file = items + "/A.nii.gz"
                B_file = items + "/B.nii.gz"
                if os.path.exists(A_file) and os.path.exists(B_file):

                    shutil.copyfile(A_file, siena_check + mse + ".nii.gz")
                    shutil.copyfile(B_file, siena_check + mse + ".nii.gz")
                    A_check = str(check_for_resampling_align(A_file.replace(".nii","_new.nii")))
                    B_check = str(check_for_resampling_align(B_file.replace(".nii", "_new.nii")))
                    if A_check == "False" or B_check == "False":
                        check = False
    return(check)




def get_msid(mse):
    cmd = ["ms_get_patient_id", "--exam_id", mse.split("mse")[1]]
    proc = Popen(cmd, stdout=PIPE)
    output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][-1][2].split("'")[-1]
    return output

def get_date(mse):
    import subprocess
    date = ""
    proc = subprocess.Popen(["ms_get_phi", "--examID", mse, "-p",password],stdout=subprocess.PIPE)
    for line in proc.stdout:
        line = str(line.rstrip())
        if "StudyDate" in   line:
            date=   line.split()[-1].lstrip("b'").rstrip("'")
            print("Date", date)
    return date

def write_csv(c, out):
    df = pd.read_csv("{}".format(c))
    for idx in range(len(df)):
        msid = "ms" + str(df.loc[idx, 'msid']).replace("ms", "").lstrip("0")
        #date = str(df.loc[idx, 'date']).split(".0")[0]
        date = ""
        #mse = "mse" + str(df.loc[idx, 'mse']).replace("mse", "").lstrip("0")
        mse = df.loc[idx, 'mse']
        if str(mse).startswith("mse"):
            mse ="mse"+ str(mse).replace("mse","").lstrip("0")
            print(mse)
            mse1 = df.loc[idx, "mse1"]
            mse2 = df.loc[idx, 'mse2']
            #bv = df.loc[idx, "V Scale"]
            #
            #first = df.loc[idx, 'Left-Caudate']
            #print(first)
            #pbvc = df.loc[idx,'pbvc']
            #if str(mse).startswith("mse"):




            """if len(msid) < 3:
                msid = get_msid(mse)
            if len(date) < 3:
                date = get_date(mse)
            df.loc[idx, "date"] = date
            df.loc[idx, "msid"] = msid
            df.loc[idx, "mse"] = mse



            df.loc[idx, 'T1'] = get_modality(mse, "T1")
            df.loc[idx, 'T2'] = get_modality(mse, "T2")
            df.loc[idx, 'FLAIR'] = get_modality(mse, "FLAIR")
            df.loc[idx, "T1_Gad"] = get_modality(mse, "T1_Gad")
            df.loc[idx, "Software"] = get_scanner_info(mse, "SoftwareVersions")
            df.loc[idx, "Scanner"] = get_scanner_info(mse, "StationName")


            df.loc[idx, "check dicom"] = get_dicom(mse)
            df.loc[idx, "check nifti"] = get_nifti(mse)
            df.loc[idx, 'check align'] = get_align(mse)
            df.loc[idx, "resample align"] = check_for_resampling_align(mse)"""
            
            
            df.loc[idx, 'Brain Stem New Calc'] = get_brainstem(mse)


            #first
            #print("FIRST", first)
            #if len(str(first)) < 4:
            #print(first, "has not been run")
            df.loc[idx, 'first'] = get_first(mse)
            F = get_first_values(mse)
            df.loc[idx, 'first'] = get_first(mse)
            df.loc[idx, 'Left-Thalamus-Proper'] = F[0]
            df.loc[idx, 'Left-Caudate'] = F[1]
            df.loc[idx, 'Left-Putamen'] = F[2]
            df.loc[idx, 'Left-Pallidum'] = F[3]
            df.loc[idx, 'Left-Hippocampus'] = F[4]
            df.loc[idx, 'Left-Amygdala'] = F[5]
            df.loc[idx, 'Left-Accumbens'] = F[6]
            df.loc[idx, 'Right-Thalamus-Proper'] = F[7]
            df.loc[idx, 'Right-Caudate'] = F[8]
            df.loc[idx, 'Right-Putamen'] = F[9]
            df.loc[idx, 'Right-Pallidum'] = F[10]
            df.loc[idx, 'Right-Hippocampus'] = F[11]
            df.loc[idx, 'Right-Amygdala'] = F[12]
            df.loc[idx, 'Right-Accumbens'] = F[13]
            df.loc[idx, 'Brain Stem'] = F[14]

            #sienax
            #if len(str(bv)) < 5:
            SX = get_sienax(mse)
        #df.loc[idx, "lst check"] = get_lst(mse)
        #df.loc[idx, "sienax_long"] = sienax_long(msid, mse)
        #df.loc[idx, "resample sienax"] = check_for_resampling_sienax(mse)
            df.loc[idx, 'sienax'] = SX[0]
            df.loc[idx, 'V Scale'] = SX[1]
            df.loc[idx, 'pGM'] = SX[2]
            df.loc[idx, 'CSF'] = SX[3]
            df.loc[idx, 'GM'] = SX[4]
            df.loc[idx, 'WM'] = SX[5]
            df.loc[idx, "BV"] = SX[6]
            df.loc[idx, "Lesion"] = SX[7]


            #siena
            #if len(str(pbvc)) < 4:
            Siena = get_siena_data(msid, mse1, mse2)
            df.loc[idx, "resample siena"] = check_for_resampling_siena(msid,mse)
            df.loc[idx, "Siena"] = Siena[2]
            df.loc[idx, "pbvc"] = Siena[0]
            #df.loc[idx, "mse2 t1"] = Siena[1]

            try:
                if str(mse2).startswith("mse"):

                    df.loc[idx, "mse2 Software"] = get_scanner_info(mse2, "SoftwareVersions")
                    df.loc[idx, "mse2 Scanner"] = get_scanner_info(mse2, "StationName")
                    df.loc[idx, "MSID - mse2"] = get_msid(mse2)
            except:
                pass



    df.to_csv(out)


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
