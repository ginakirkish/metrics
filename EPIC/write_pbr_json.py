
import pbr
import os
from glob import glob
from pbr.base import _get_output
from subprocess import Popen, PIPE
import json
from nipype.utils.filemanip import load_json
heuristic = load_json(os.path.join(os.path.split(pbr.__file__)[0], "heuristic.json"))["filetype_mapper"]
from pbr.workflows.nifti_conversion.utils import description_renamer
import nibabel as nib
import numpy as np
from pbr.config import config
import freesurfer_stats
from freesurfer_stats import CorticalParcellationStats

import pandas as pd

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


def get_t1_series(mse):
    t1_series_num = "1"
    if os.path.exists(_get_output(mse)+"/"+mse+"/nii/status.json"):
        try:
            with open(_get_output(mse)+"/"+mse+"/nii/status.json") as data_file:
                data = json.load(data_file)
                if len(data["t1_files"]) == 0:
                    t1_series_num = "1"
                else:
                    t1_series_num = data["t1_files"][-1].split("-")[2].lstrip("0")
        except:
            pass
    return t1_series_num


def get_scanner_info(mse, x, t1_series_num):
    info = ""
    try:

        dicom = glob("/working/henry_temp/PBR/dicoms/{0}/E*/{1}/*.DCM".format(mse, t1_series_num))[0]
        cmd = ["dcmdump", dicom]
        proc = Popen(cmd, stdout=PIPE)
        output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
        for line in output:
            if x in line:
                if x == "PatientComments":
                    info = str(line).replace("'","").replace(",","").split("[")[2].split("]")[0]
                else:
                    dicom_info = str(str(line[2:]).split(']')[0].split('[')[2:]).replace('[',"").replace(']','').replace('"','').replace("'","")
                    info = dicom_info

    except:
        pass

    return info

def get_dicom_hdr(mse, t1_series_num):
    uctable = dist = scanreg = ""
    try:
        dicom = glob("/working/henry_temp/PBR/dicoms/{0}/E*/{1}/*.DCM".format(mse, t1_series_num))[0]
        cmd = ["dicom_hdr", "-sexinfo", dicom] #, "|","grep", "sDistortionCorrFilter.ucMode"]
        proc = Popen(cmd, stdout=PIPE)
        output =[l.decode('latin-1').split() for l in proc.stdout.readlines()[:]]
        for line in output:
            if len(line) >= 1:
                newline = line[0]
                if "ucTablePositioningMode" in newline:
                    uctable = line[2]
                    print("ucTable:", uctable)
                if "DistortionCorrFilter.ucMode" in newline:
                    dist = line[2]
                    print("DistortionCorrFilter:", dist)
                if "lScanRegionPosTra" in newline:
                    scanreg = line[2]
                    print("lScanRegionPosTra:", scanreg)

    except:
        pass

    return uctable, dist, scanreg




def get_coil_channel(mse, t1_series_num):
    coil = ""
    dicom = glob("/working/henry_temp/PBR/dicoms/{0}/E*/{1}/*.DCM".format(mse, t1_series_num))
    if len(dicom)>0:

        cmd = ["gdcmdump", dicom[0]]
        proc = Popen(cmd, stdout=PIPE)
        output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
        for line in output:
            line = str(line)
            if "(0051,100f)" in line:
                if "HC1-7" in line:
                    coil = "64-Channel"
                elif "HE1-4":
                    coil = "20-Channel"

                else:
                    coil = line
    return coil

def get_first_values(mse):
    metrics = ""
    status = "{}/{}/first_all/status.json".format(_get_output(mse),mse)
    if os.path.exists(status):
        with open(status) as json_file:
            data = json.load(json_file)
            for metrics in data['metrics']:
                print(metrics)
    return metrics


def get_sienax(mse):
    les_vol=sienax_label=sienax=VS =PG =VCSF =GM=WM= BV=num_lesions =""
    sienax_optibet = glob("/{0}/{1}/sienax_optibet/ms*/report.sienax".format(_get_output(mse),mse))
    if len(sienax_optibet) >= 1:
        sienax = sienax_optibet[-1]
        with open(sienax, "r") as f:
            lines = [line.strip() for line in f.readlines()]
            for line in lines:
                try:
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
                except:
                    pass

        lm = sienax.replace("report.sienax","/lesion_mask.nii.gz")
        if os.path.exists(lm):
            try:
                img = nib.load(lm)
                data = img.get_data()
                les_vol = np.sum(data)
                num_lesions = count_les(lm)
                #num_lesions=""
            except:
                pass
    return [VS, PG, VCSF, GM, WM, BV, str(les_vol), str(num_lesions)]


def count_les(lm):
    count = lm.replace("lesion_mask.nii.gz","count.txt")
    cmd = ["cluster", "--in={}".format(lm), "--thresh=.7", "--oindex=les", "--minextent=10", "--olmax={}".format(count)]
    Popen(cmd).wait()
    try:
        open_file=open(count,'r')
        file_lines=open_file.readlines()
        loc_file = file_lines[2].strip()#[0] + file_lines[2].strip()[1] + file_lines[2].strip()[2]
        count = str(str(loc_file).replace("	","x").split("x")[0])
        print("LESION:",count )
    except:
        pass
    return count


def get_siena_data(msid, mse):
    pbvc = subjects = ""
    out = config["long_output_directory"]
    siena = glob('{}/{}/siena_optibet/mse*__{}/report.siena'.format(out, msid, mse))
    if len(siena)>0:
        siena=siena[0]
        with open(siena, "r") as f:
            lines = [line.strip() for line in f.readlines()]
            for line in lines:
                if line.startswith("finalPBVC"):
                    pbvc =  line.split()[1]
                    subjects = siena.split('/')[7]

    return [pbvc, subjects]

def get_msid(mse):
    cmd = ["ms_get_patient_id", "--exam_id", mse.split("mse")[1]]
    proc = Popen(cmd, stdout=PIPE)
    msid = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][-1][2].split("'")[-1]
    return msid

def get_t1(mse):
    t1_file = ""
    if os.path.exists(_get_output(mse)+"/"+mse+"/alignment/status.json"):
        with open(_get_output(mse)+"/"+mse+"/alignment/status.json") as data_file:
            try:
                data = json.load(data_file)
                if len(data["t1_files"]) > 0:
                    t1_file = data["t1_files"][-1].split('/')[-1].replace(".nii.gz","")
            except:
                pass
    return t1_file



def get_value(structure, line):
    volume = "x"
    if structure in line:
        first_letter = structure[0:3]
        line = line.split(" ")
        for items in line:
            if items.startswith(first_letter):
                break
            elif "." in items:
                volume = items
    return volume

def calc_fs_vol(stats):
    intrcranial = cortex= brain_seg= gm= wm= supra= LILV= RILV= L_cere= R_cere= L_thal= R_thal= L_caud= R_caud= L_put= R_put= L_acc= R_acc= L_venDC= R_venDC= OC=L_pall= R_pall= csf= L_hipp= R_hipp= L_amy= R_amy= third_ven= forth_ven= BS=""
    with open(stats, "r") as f:
         for line in f:
            #print(line)
            if "EstimatedTotalIntraCranialVol" in line:
                print(line.split(',')[3])
                intrcranial = line.split(',')[3].replace(" ","")
            if "Measure Cortex, CortexVol," in line:
                cortex = line.split(',')[3].replace(" ","")
            if "BrainSeg, BrainSegVol, Brain Segmentation Volume, " in line:
                brain_seg = line.split(',')[3].replace(" ","")
            if "Total gray matter volume" in line:
                gm = line.split(',')[3].replace(" ","")
            if  "SupraTentorial, SupraTentorialVol, Supratentorial volume" in line:
                supra = line.split(',')[3].replace(" ","")
            if "Total cortical white matter volume" in line:
                wm = line.split(',')[3].replace(" ","")
            x = get_value("Left-Lateral-Ventricle", line)
            if not x =="x":
                LLV = x
            x = get_value("Left-Inf-Lat-Vent", line)
            if not x =="x":
                LILV = x
            x= get_value( "Left-Cerebellum-Cortex" , line)
            if not x =="x":
                L_cere=  x
            x= get_value( "Left-Thalamus-Proper" , line)
            if not x =="x":
                L_thal = x
            x= get_value( "Left-Caudate" , line)
            if not x =="x":
                L_caud = x
            x= get_value( "Left-Putamen" , line)
            if not x =="x":
                L_put = x
            x= get_value( "Left-Pallidum" , line)
            if not x =="x":
                L_pall= x
            x= get_value( "3rd-Ventricle" , line)
            if not x =="x":
                third_ven = x
            x= get_value( "4th-Ventricle" , line)
            if not x =="x":
                forth_ven = x
            x= get_value( "Brain-Stem" , line)
            if not x =="x":
                BS = x
            x= get_value( "Left-Hippocampus" , line)
            if not x =="x":
                L_hipp = x
            x= get_value( "Left-Amygdala" , line)
            if not x =="x":
                L_amy = x
            x= get_value( "Right-Amygdala" , line)
            if not x =="x":
                R_amy = x
            x= get_value( "CSF" , line)
            if not x =="x":
                csf = x
            x= get_value( "Left-Accumbens-area" , line)
            if not x =="x":
                L_acc = x
            x= get_value( "Left-VentralDC" , line)
            if not x =="x":
                L_venDC = x
            x= get_value( "Right-Lateral-Ventricle" , line)
            if not x =="x":
                RLV = x
            x= get_value( "Right-Inf-Lat-Vent" , line)
            if not x =="x":
                RILV = x
            x= get_value( "Right-Cerebellum-Cortex" , line)
            if not x =="x":
                R_cere = x
            x= get_value( "Right-Thalamus-Proper" , line)
            if not x =="x":
                R_thal = x
            x= get_value( "Right-Caudate" , line)
            if not x =="x":
                R_caud = x
            x= get_value( "Right-Putamen" , line)
            if not x =="x":
                R_put = x
            x= get_value( "Right-Accumbens-area" , line)
            if not x =="x":
                R_acc = x
            x= get_value( "Right-VentralDC" , line)
            if not x =="x":
                R_venDC = x
            x= get_value( "Right-Pallidum" , line)
            if not x =="x":
                R_pall= x
            x= get_value( "Optic-Chiasm" , line)
            if not x =="x":
                OC = x
            x= get_value( "Right-Hippocampus" , line)
            if not x =="x":
                R_hipp = x

    return intrcranial, cortex, brain_seg, gm, wm, supra,LLV, RLV, LILV, RILV, L_cere, R_cere,\
           L_thal, R_thal, L_caud, R_caud, L_put, R_put, L_acc, R_acc, L_venDC, R_venDC,\
           OC,L_pall, R_pall, csf, L_hipp, R_hipp, L_amy, R_amy, third_ven, forth_ven, BS

def get_t1(mse):
    t1_file = ""
    if os.path.exists(_get_output(mse)+"/"+mse+"/alignment/status.json"):
        with open(_get_output(mse)+"/"+mse+"/alignment/status.json") as data_file:
            try:
                data = json.load(data_file)
                if len(data["t1_files"]) > 0:
                    t1_file = data["t1_files"][-1]
            except:
                pass
    return t1_file




"""df = pd.read_csv("/home/sf522915/Documents/FINAL-feb2020.csv")
import pandas as pd
for idx in range(len(df)):
        msid = df.loc[idx, 'msid']
        mse = df.loc[idx, 'mse']
        pbr = _get_output(mse)+'/'+ mse +"/alignment/"
        """



def run(mse, pbr):

    data = {}
    data["Sequences"] = []
    data["Sequences"].append({
        "T1":    get_modality(mse, "T1"),
        "T2":    get_modality(mse, "T2"),
        "FLAIR": get_modality(mse, "FLAIR"),
        "Gad":   get_modality(mse, "T1_Gad"),
        "PSIR":  get_modality(mse, "C2_3_psir_PSIR"),
        "NODDI": get_modality(mse, "NODDI"),
        "MT_pulse_on":get_modality(mse,"MT_pulse_on"),
        "DWI":        get_modality(mse,"DWI")
    })

    t1_series_num = str(get_t1_series(mse))
    uctable, dist, scanreg = get_dicom_hdr(mse, t1_series_num)
    print("*******************",get_scanner_info(mse, "PatientComments", t1_series_num),)
    data["Scanner_Info"] = []
    data["Scanner_Info"].append({
        "Software":          get_scanner_info(mse, "SoftwareVersions",t1_series_num),
        "Scanner":           get_scanner_info(mse, "StationName", t1_series_num),
        "BodyPartExamined":  get_scanner_info(mse, "BodyPartExamined", t1_series_num),
        "Transmit Coil":     get_scanner_info(mse, "TransmitCoilName", t1_series_num),
        "Receive Coil":      get_scanner_info(mse, "ReceiveCoilName", t1_series_num),
        "Coil Channel":      get_coil_channel(mse, t1_series_num),
        "Study Comment":     get_scanner_info(mse, "PatientComments", t1_series_num),
        "Distortion Correction": dist,
        "ucTablePositionMode": uctable,
        "1ScanRegionPosTra": scanreg
    })



    SX = get_sienax(mse)
    data["SIENAX"] = []
    data["SIENAX"].append({
        'V Scale':   SX[0],
        'pGM':       SX[1],
        'CSF':       SX[2],
        'GM':        SX[3],
        'WM':        SX[4],
        "BV":        SX[5],
        "Lesion Vol":SX[6],
        "Lesion Num":SX[7]
    })


    data["First"] = []
    data["First"].append(
        get_first_values(mse)
    )
    msid = ""
    try:
        msid = get_msid(mse)
    except:
        pass
    siena = get_siena_data(msid, mse)
    data["SIENA"] = []
    data["SIENA"].append({
    "pbvc": siena[0],
    "timepoints": siena[1]

    })




    t1 = get_t1(mse).split('/')[-1].replace(".nii.gz","")
    stats = os.path.join("/data/henry6/PBR/surfaces/",t1,"stats","aseg.stats")
    print(stats)
    if os.path.exists(stats):
        intrcranial, cortex, brain_seg, gm, wm, supra,LLV,RLV, LILV, RILV, L_cere, \
        R_cere, L_thal, R_thal, L_caud, R_caud, L_put, R_put, L_acc, R_acc,\
        L_venDC, R_venDC, OC, L_pall, R_pall, csf, L_hipp, R_hipp, L_amy, \
        R_amy, third_ven, forth_ven, BS = calc_fs_vol(stats)

        data["freesurfer"] = []
        data["freesurfer"].append({
            "eTIV" : intrcranial,
            "Cortex" : cortex,
            "Gray Matter" : gm,
            "White Matter" : wm,
            "Supratentorial" : supra,
            "LLV":LLV,
            "RLV":RLV,
            "Left-Inf-Lat-Vent" : LILV,
            "Right-Inf-Lat-Vent":RILV,
            "Left_Cerebellum": L_cere,
            "Right-Cerebellum":R_cere,
            "Left-Thalamus": L_thal,
            "Right-Thalamus":R_thal,
            "Left-Caudate": L_caud,
            "Right-Caudate":R_caud,
            "Left-Putamen":L_put,
            "Right-Putamen":R_put,
            "Left-Accumbens":L_acc,
            "Right-Accumbens":R_acc,
            "Left-ventDC": L_venDC,
            "Right-ventDC":R_venDC,
            "Optic Chiasm":OC,
            "Left-Pallidum": L_pall,
            "Right-Pallidum":R_pall,
            "CSF":csf,
            "Left-Hippocampus":L_hipp,
            "Right-Hippocampus":R_hipp,
            "Left-Amygdala":L_amy,
            "Right-Hippocampus":R_amy,
            "3rd-Vent":third_ven,
            "4th-Vent":forth_ven,
            "Brain-Stem":BS

        })

    with open('{}/{}/metrics.json'.format(_get_output(mse),mse), 'w') as outfile:
        json.dump(data, outfile,indent=4)




"""henry = ["henry11"]
for h in henry:
    for mse in os.listdir("/data/"+ h+ "/PBR/subjects/"):
        pbr = "/data/"+ h+ "/PBR/subjects/" + mse +"/alignment/"""

df = pd.read_csv("/home/sf522915/Documents/FINAL_MARCH2020.csv")
for idx in range(len(df)):
        msid = df.loc[idx, 'msid']
        mse = df.loc[idx, 'mse']
        print(msid, mse)

        """try:
            num = int(mse.split("mse")[-1])
        except:
            num = "1"
            pass"""

        if mse.startswith("mse") :#and os.path.exists(pbr):#nd num >9500:
            print(mse)
            met = "{}/{}/metrics.json".format(_get_output(mse),mse)
            #if not os.path.exists("{}/{}metrics.json".format(_get_output(mse),mse)):
            print(mse)

            if os.path.exists(met):
                run(mse, pbr)
                with open(met) as data_file:
                    data = json.load(data_file)
                    if len(data["Scanner_Info"])>0:
                        scan_info = data["Scanner_Info"]
                        for items in  scan_info:
                            header = items.keys()
                            if "Study Comment" in header:
                                print(mse, "COMPLETED")
                            else:
                                run(mse, pbr)

            else:
                run(mse, pbr)


