
import argparse
import pbr
import os
from glob import glob
from pbr.base import _get_output
import json
from subprocess import Popen, PIPE
from getpass import getpass
#from subprocess import check_output, check_call
import json
#import pandas as pd
from nipype.utils.filemanip import load_json
heuristic = load_json(os.path.join(os.path.split(pbr.__file__)[0], "heuristic.json"))["filetype_mapper"]
from pbr.workflows.nifti_conversion.utils import description_renamer

password = getpass("mspacman password: ")
working = "/working/henry_temp/PBR/dicoms/"


for msid in os.listdir("/data/henry6/mindcontrol_ucsf_env/watchlists/long/VEO/all/"):
    msid = msid.split(".txt")[0]
    cmd = ["ms_get_patient_imaging_exams", "--patient_id", msid.split("ms")[1]]
    print(cmd)
    proc = Popen(cmd, stdout=PIPE)
    lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[5:]]
    print(lines)





def get_dicom(mse):
    try:
        dicom = glob(working + "/{0}/E*".format(mse))[0]
        print("DICOM DIRECTORY:", dicom)
    except:
        cmd = ["ms_dcm_qr", "-t", mse.split("mse")[1], "-e", working + mse]
        print(cmd)
        Popen(cmd).wait()
        try:
            glob(working + "/{0}/E*".format(mse))[0]
            print(mse, "Successfully retrieved dicom from mspacman")
        except:
            print(mse, "Error retrieving dicom from mspacman, need to investigate further")
            with open("/data/henry6/gina/Error_log/dicom.txt", "w") as text_file:
                text_file.write(mse + "\n")
            pass
        pass


def get_modality(mse):
    num = mse.split("mse")[-1]
    cmd = ["ms_dcm_exam_info", "-t", num]
    proc = Popen(cmd, stdout=PIPE)
    lines = [description_renamer(" ".join(l.decode("utf-8").split()[1:-1])) for l in proc.stdout.readlines()[8:]]
    print("******These are the sequence names coming from the dicom images*****")
    for items in lines:
        print(items)
    print("********************************************************************")
    sequences  = ["T1", "T2", "FLAIR", "T1_Gad"]
    for sq in sequences:
        print("checking for...", sq)
        sequence_name = ""
        nii_type = sq
        if nii_type:
            try:
                sequence_name = filter_files(lines, nii_type, heuristic)[0]
                print(sequence_name, "This is the {0}".format(sq))
            except:
                print(mse, "No {0} in dicom identified by the heuristic...Please check sequnces and heuristic".format(sq))

                pass
        if len(sequence_name) > 1:
            print("checking for sequence names in nifti and align folders")
            check_for_sq_names(mse, sq, "/nii/", sequence_name)
            check_for_sq_names(mse, sq, "/alignment/", sequence_name)

    get_nifti(mse)
    get_align(mse)


def filter_files(descrip,nii_type, heuristic):
    output = []
    for i, desc in enumerate(descrip):
        if desc in list(heuristic.keys()):
            if heuristic[desc] == nii_type:
                 output.append(desc)
    return output


def run_nifti(mse):
    try:
        cmd = ["pbr", mse, "-w", "nifti", "-R"]
        print(cmd)
        Popen(cmd).wait()
    except:
        with open("/data/henry6/gina/Error_log/nifti.txt", "w") as text_file:
            text_file.write(mse + "\n")
        pass



def run_align(mse):
    try:
        cmd = ["pbr", mse, "-w", "align", "-R"]
        print(cmd)
        Popen(cmd).wait()
    except:
        with open("/data/henry6/gina/Error_log/align.txt", "w") as text_file:
            text_file.write(mse + "\n")
        pass

def check_in_nii_align(sq, x, mse, data, pipeline, sequence_name):
    if pipeline == "/nifti/":
        if not sequence_name in data[x]:
            print("No {0} in nifti status file, but {1} in dicom heuristic... re-running nifti conversion".format(sequence_name, sq))
            run_nifti(mse)
        else:
            print("THE {0} FILE EXISTS... ready to run align".format(sq))

    if pipeline == "/align/":
        if not sequence_name in data[x]:
            print("No {0} in align status file, but {1} in dicom heuristic... re-running alignment".format(sequence_name, sq))
            run_align(mse)
        else:
            print("THE {0} FILE EXISTS...".format(sq))


def check_for_sq_names(mse, sq, pipeline, sequence_name ):
    nifti_align = _get_output(mse)+"/"+mse+ pipeline + "/status.json"
    if os.path.exists(nifti_align):
        with open(nifti_align) as data_file:
            data = json.load(data_file)
            if sq == "T1":
                check_in_nii_align(sq, "t1_files", mse, data, pipeline, sequence_name)
            if sq == "T2":
                check_in_nii_align(sq, "t2_files", mse, data, pipeline, sequence_name)
            if sq == "FLAIR":
                check_in_nii_align(sq, "flair_files", mse, data, pipeline, sequence_name)
            if sq == "T1_Gad":
                check_in_nii_align(sq, "gad_files", mse, data, pipeline, sequence_name)

def get_nifti(mse):
    nifti = _get_output(mse)+"/"+mse+"/nii/status.json"
    if not os.path.exists(nifti):
        run_nifti(mse)
    else:
        print(mse, "NIFTI HAS BEEN SUCCESSFULLY RUN")


def get_align(mse):
    align = _get_output(mse)+"/"+mse+"/alignment/status.json"
    if not os.path.exists(align):
        print("ALIGN DIRECTORY DOES NOT EXIST")
        run_align(mse)
    else:
        print(mse, "ALIGN HAS BEEN SUCCESSFULLY RUN", align)

def check_pbr(mse):
    print("running...", mse)
    get_dicom(mse)
    get_modality(mse)







