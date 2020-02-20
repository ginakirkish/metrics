
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
from freesurfer_stats import CorticalParcellationStats



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
                dicom_info = str(str(line[2:]).split(']')[0].split('[')[2:]).replace('[',"").replace(']','').replace('"','').replace("'","")
                info = dicom_info
    except:
        pass

    return info



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



def get_fs_data(mse):
    fs_path = "{}/{}/stats/aseg.stats".format(config["subjects_directory"], get_t1(mse), "/lh.aparc.stats")
    print(fs_path)
    stats = CorticalParcellationStats.read(fs_path)
    #whole_brain = stats.whole_brain_measurements['estimated_total_intracranial_volume_mm^3']
    #print(whole_brain)


henry = ["henry7","henry11"]
for h in henry:
    for mse in os.listdir("/data/"+ h+ "/PBR/subjects/"):
        pbr = "/data/"+ h+ "/PBR/subjects/" + mse +"/alignment/"
        if mse.startswith("mse") and os.path.exists(pbr):
            print(mse)
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
            data["Scanner_Info"] = []
            data["Scanner_Info"].append({
                "Software":          get_scanner_info(mse, "SoftwareVersions",t1_series_num),
                "Scanner":           get_scanner_info(mse, "StationName", t1_series_num),
                "BodyPartExamined":  get_scanner_info(mse, "BodyPartExamined", t1_series_num),
                "Transmit Coil":     get_scanner_info(mse, "TransmitCoilName", t1_series_num),
                "Receive Coil":      get_scanner_info(mse, "ReceiveCoilName", t1_series_num),
                "Coil Channel":      get_coil_channel(mse, t1_series_num)
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

            msid = get_msid(mse)
            siena = get_siena_data(msid, mse)
            data["SIENA"] = []
            data["SIENA"].append({
                "pbvc": siena[0],
                "timepoints": siena[1]
            })

            #get_fs_data(mse)

            with open('{}/{}/metrics.json'.format(_get_output(mse),mse), 'w') as outfile:
                json.dump(data, outfile,indent=4)



