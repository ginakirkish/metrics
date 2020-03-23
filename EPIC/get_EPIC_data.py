
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
from scipy.ndimage.measurements import label

#password = getpass("mspacman password: ")

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

def get_first_values(mse):
    L_thal=L_caud=L_put=L_pall=L_hipp= L_amy= L_acc=  R_thal= R_caud= R_put=R_pall= R_hipp= R_amy= R_acc=BS = ''
    metrics = ""
    status = "{}/{}/first_all/status.json".format(_get_output(mse),mse)
    if os.path.exists(status):
        with open(status) as f:

            first_dict = json.load(f)
            try:
                metrics = first_dict['metrics'][0]

                L_thal = metrics['Left-Thalamus-Proper']
                L_caud = metrics['Left-Caudate']
                L_put  = metrics['Left-Putamen']
                L_pall = metrics['Left-Pallidum']
                L_hipp = metrics['Left-Hippocampus']
                L_amy  = metrics['Left-Amygdala']
                L_acc  = metrics['Left-Accumbens-area']
                R_thal = metrics['Right-Thalamus-Proper']
                R_caud = metrics['Right-Caudate']
                R_put  = metrics['Right-Putamen']
                R_pall = metrics['Right-Pallidum']
                R_hipp = metrics['Right-Hippocampus']
                R_amy  = metrics['Right-Amygdala']
                R_acc  = metrics['Right-Accumbens-area']
                BS  = metrics['Brain-Stem /4th Ventricle']
            except:
                pass

    else:
        first = glob("{}/{}/first_all/ms*firstsegs.nii.gz".format(_get_output(mse),mse))
        if len(first)>0:
            first = first[0]
            img = nib.load(first).get_data()

            L_caud = len(np.where(img == 11)[0])
            L_put =  len(np.where(img == 12)[0])
            L_pall = len(np.where(img == 13)[0])
            L_hipp = len(np.where(img == 17)[0])
            L_amy =  len(np.where(img == 18)[0])
            L_acc =  len(np.where(img == 26)[0])

            R_caud = len(np.where(img == 50)[0])
            R_put =  len(np.where(img == 51)[0])
            R_pall = len(np.where(img == 52)[0])
            R_hipp = len(np.where(img == 17)[0])
            R_amy =  len(np.where(img == 54)[0])
            R_acc =  len(np.where(img == 58)[0])
            BS =     len(np.where(img == 16)[0])

            print(L_caud)
            print(L_put)
            print(L_pall)

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
    sienax_label, sienax, VS, PG, VCSF, GM, WM, BV, num_lesions ="", "", "", "", "", "", "", "", ""
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
    else:
        sienax = ""
        sienax_label = ""

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
            try:
                img = nib.load(lm)
                data = img.get_data()
                les_vol = np.sum(data)
                data = np.array(img.get_data())
                labeled_array, num_lesions = label(data)
                print("################# LESION NUMBER", num_lesions)
            except:
                pass
    return [sienax_label, VS, PG, VCSF, GM, WM, BV, les_vol,num_lesions]



def get_siena_data(msid, mse, mse2):

    henry10 = "/data/henry10/PBR_long/subjects/" + msid + '/siena_optibet/'
    siena_label = final_pbvc = ""
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
                                final_pbvc =  line.split()[1]


    return [final_pbvc, siena_label]

def get_scanner_info(mse, x, t1_series_num):
    info = ""
    try:
        dicom = glob("/working/henry_temp/PBR/dicoms/{0}/E*/{1}/*.DCM".format(mse, t1_series_num))[0]
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

def read_siena_html(msid, mse1, mse2):
    siena_cmd = ""
    siena_html = glob("/data/henry10/PBR_long/subjects/{}/siena_optibet/{}__{}/report.html".format(msid, mse1, mse2))
    if len(siena_html)>0:
        siena_html = siena_html[0]
        with open("{}".format(siena_html),"r") as f:
            for line in f.readlines():
                if "siena_optibet" in line:
                    siena_cmd = "siena" + line.split("siena")[-1].split("<TD ALIGN=RIGHT>")[0]
                    siena_cmd = str(siena_cmd)
                    print("^^^^^^^^^^^^^^^^^", siena_cmd, "^^^^^^^^^^^^^^^^^")
    return siena_cmd

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

def get_t1_series(mse):
    t1_series_num = "1"
    if os.path.exists(_get_output(mse)+"/"+mse+"/nii/status.json"):
        try:
            with open(_get_output(mse)+"/"+mse+"/nii/status.json") as data_file:
                data = json.load(data_file)
                #print(data)
                if len(data["t1_files"]) == 0:
                    t1_series_num = "1"
                else:
                    t1_series_num = data["t1_files"][-1].split("-")[2].lstrip("0")
        except:
            pass
    return t1_series_num


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
            mse1 = df.loc[idx, "mse_bl"]
            mse2 = df.loc[idx, 'mse']
            bv = df.loc[idx, "V Scale"]
            #
            first = df.loc[idx, 'Left-Caudate']
            #print(first)
            pbvc = df.loc[idx,'pbvc']
            #t1 = df.loc[idx, "T1"]
            #if str(mse).startswith("mse"):
            t1_series_num = str(get_t1_series(mse))
            """df.loc[idx, "check dicom"] = get_dicom(mse)
            df.loc[idx, "check nifti"] = get_nifti(mse)
            df.loc[idx, 'check align'] = get_align(mse)

            if len(msid) < 3:
                msid = get_msid(mse)
            if len(date) < 3:
                date = get_date(mse)
            df.loc[idx, "date"] = date
            df.loc[idx, "msid"] = msid
            df.loc[idx, "mse"] = mse
            #if len(str(t1))<3:"""


            """df.loc[idx, 'T1'] = get_modality(mse, "T1")
            df.loc[idx, 'T2'] = get_modality(mse, "T2")
            df.loc[idx, 'FLAIR'] = get_modality(mse, "FLAIR")
            df.loc[idx, "T1_Gad"] = get_modality(mse, "T1_Gad")
            df.loc[idx, "PSIR C23 MAG"] = get_modality(mse, "C2_3_psir_MAG")
            df.loc[idx, "PSIR C34 MAG"] = get_modality(mse, "C3_4_psir_MAG")
            df.loc[idx, "PSIR psir"] = get_modality(mse, "C2_3_psir_PSIR")
            df.loc[idx, "PSIR C34 psir"] = get_modality(mse, "C3_4_psir_PSIR")

            print(t1_series_num, "&&&&&&&&&&&&&&&&")

            df.loc[idx, "Software"] = get_scanner_info(mse, "SoftwareVersions",t1_series_num)
            df.loc[idx, "Scanner"] = get_scanner_info(mse, "StationName", t1_series_num)
            df.loc[idx, "BodyPartExamined"] = get_scanner_info(mse, "BodyPartExamined", t1_series_num)
            df.loc[idx, "Transmit Coil"] = get_scanner_info(mse, "TransmitCoilName", t1_series_num)
            df.loc[idx, "Receive Coil"] = get_scanner_info(mse, "ReceiveCoilName", t1_series_num)
            coil = ""
            dicom = glob("/working/henry_temp/PBR/dicoms/{0}/E*/{1}/*.DCM".format(mse, t1_series_num))[0]
            cmd = ["gdcmdump", dicom]
            proc = Popen(cmd, stdout=PIPE)
            output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
            for line in output:
                line = str(line)
                #print(line)
                if "(0051,100f)" in line or "0051,100f" in line or line.startswith("['(0051,100f)") :
                    #dicom_info = str(str(line[2:]).split(']')[0].split('[')[2:]).replace('[',"").replace(']','').replace('"','').replace("'","")
                    #info = dicom_info
                    #print("%%%%%",info)
                    if "HC1-7" in line:
                        coil = "64-Channel"
                    elif "HE1-4":
                        coil = "20-Channel"

                    else:
                        coil = line
            df.loc[idx, "Coil 0051"] = coil
            print("**********",line)"""




            first = get_first_values(mse)
            if len(first)>0:
                df.loc[idx, 'first'] = get_first(mse)
                df.loc[idx, 'Left-Thalamus-Proper'] = first[0]
                df.loc[idx, 'Left-Caudate'] = first[1]
                df.loc[idx, 'Left-Putamen'] = first[2]
                df.loc[idx, 'Left-Pallidum'] = first[3]
                df.loc[idx, 'Left-Hippocampus'] = first[4]
                df.loc[idx, 'Left-Amygdala'] = first[5]
                df.loc[idx, 'Left-Accumbens'] = first[6]
                df.loc[idx, 'Right-Thalamus-Proper'] = first[7]
                df.loc[idx, 'Right-Caudate'] = first[8]
                df.loc[idx, 'Right-Putamen'] = first[9]
                df.loc[idx, 'Right-Pallidum'] = first[10]
                df.loc[idx, 'Right-Hippocampus'] = first[11]
                df.loc[idx, 'Right-Amygdala'] = first[12]
                df.loc[idx, 'Right-Accumbens'] = first[13]
                df.loc[idx, 'Brain Stem'] = first[14]




            """df.loc[idx, "check dicom"] = get_dicom(mse)
            df.loc[idx, "check nifti"] = get_nifti(mse)
            df.loc[idx, 'check align'] = get_align(mse)
            #df.loc[idx, "resample align"] = check_for_resampling_align(mse)


            

            #first
            #print("FIRST", first)
            if len(str(first)) < 4:
                #print(first, "has not been run")
                df.loc[idx, 'first'] = get_first(mse)
                F = get_first_values(mse)
                df.loc[idx, 'first'] = get_first(mse)
                df.loc[idx, 'Left-Thalamus-Proper'] = first[0]
                df.loc[idx, 'Left-Caudate'] = first[1]
                df.loc[idx, 'Left-Putamen'] = first[2]
                df.loc[idx, 'Left-Pallidum'] = first[3]
                df.loc[idx, 'Left-Hippocampus'] = first[4]
                df.loc[idx, 'Left-Amygdala'] = first[5]
                df.loc[idx, 'Left-Accumbens'] = first[6]
                df.loc[idx, 'Right-Thalamus-Proper'] = first[7]
                df.loc[idx, 'Right-Caudate'] = first[8]
                df.loc[idx, 'Right-Putamen'] = first[9]
                df.loc[idx, 'Right-Pallidum'] = first[10]
                df.loc[idx, 'Right-Hippocampus'] = first[11]
                df.loc[idx, 'Right-Amygdala'] = first[12]
                df.loc[idx, 'Right-Accumbens'] = first[13]
                df.loc[idx, 'Brain Stem'] = first[14]
                #df.loc[idx, 'Brain Stem'] = get_brainstem(mse)"""

            #sienax
            if len(str(bv)) < 5:
            #try:
                SX = get_sienax(mse)
                df.loc[idx, "lst check"] = get_lst(mse)
                df.loc[idx, "sienax_long"] = sienax_long(msid, mse)
                df.loc[idx, "resample sienax"] = check_for_resampling_sienax(mse)
                df.loc[idx, 'sienax'] = SX[0]
                df.loc[idx, 'V Scale'] = SX[1]
                df.loc[idx, 'pGM'] = SX[2]
                df.loc[idx, 'CSF'] = SX[3]
                df.loc[idx, 'GM'] = SX[4]
                df.loc[idx, 'WM'] = SX[5]
                df.loc[idx, "BV"] = SX[6]
                df.loc[idx, "Lesion"] = SX[7]
                df.loc[idx, "Lesion Count"] = SX[8]
                print("^^^^^^^^^^", SX[8])
            #except:
                #pass


            #siena
            #pbvc = ""
            if len(str(pbvc)) < 4:
                Siena = get_siena_data(msid, mse1, mse2)
                df.loc[idx, "siena_cmd"] = read_siena_html(msid, mse1, mse2)
                df.loc[idx, "resample siena"] = check_for_resampling_siena(msid,mse)
                df.loc[idx, "Siena"] = Siena[1]
                df.loc[idx, "pbvc"] = Siena[0]
            #df.loc[idx, "mse2 t1"] = Siena[1]"""

            """try:
                if str(mse2).startswith("mse"):

                    df.loc[idx, "mse2 Software"] = get_scanner_info(mse2, "SoftwareVersions", t1_series_num)
                    df.loc[idx, "mse2 Scanner"] = get_scanner_info(mse2, "StationName")
                    df.loc[idx, "MSID - mse2"] = get_msid(mse2)
            except:
                pass"""

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
