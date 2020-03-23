import pbr
import os
from getpass import getpass
import json
from nipype.utils.filemanip import load_json
heuristic = load_json(os.path.join(os.path.split(pbr.__file__)[0], "heuristic.json"))["filetype_mapper"]
from pbr.workflows.nifti_conversion.utils import description_renamer
import os
from subprocess import Popen, PIPE
from glob import glob
import shutil
from pbr.base import _get_output
import json
import math
import argparse
import pandas as pd
from pbr.base import config
import subprocess
import time

password = getpass("mspacman password: ")
working = "/working/henry_temp/PBR/dicoms/"
mspac_path = "/data/henry1/mspacman_data/"


pbsdir = "/home/sf522915/pbs/"

def submit(shell_cmd):

    if '/' in shell_cmd.split(' ')[0]:
        job_name = '{}_{}'.format(shell_cmd.split(' ')[0].split('/')[-1], time.time())
    else:
        job_name = '{}_{}'.format(shell_cmd.split(' ')[0], time.time())
    print('job name', job_name)
    scriptfile = os.path.join(pbsdir, job_name+'.sh')
    fid = open(scriptfile,"w")
    fid.write("\n".join(["#! /bin/bash",
                         "#$ -V",
                         "#$ -q ms.q",
                         "#$ -l arch=lx24-amd64",
                         "#$ -v MKL_NUM_THREADS=1",
                         "#$ -l h_stack=32M",
                         "#$ -l h_vmem=5G",
                         "#$ -N {}".format(job_name),
                         "\n"]))

    fid.write("\n".join(["hostname",
                         "\n"]))


    #PIPEs the error and output to specific files in the log directory
    fid.write(shell_cmd)
    fid.close()

    # Write the qsub command line
    qsub = ["cd",pbsdir,";","/netopt/sge_n1ge6/bin/lx24-amd64/qsub", scriptfile]
    cmd = " ".join(qsub)
    print(cmd)
    # Submit the job
    print("Submitting job {} to grid".format(job_name))
    proc = subprocess.Popen(cmd,
                            stdout = subprocess.PIPE,
                            stderr = subprocess.PIPE,
                            env=os.environ,
                            shell=True,
                            cwd=pbsdir)
    stdout, stderr = proc.communicate()
    print(stdout, stderr)






def copy_mni_bl(bl_t1_mni,mse_bl):
    baseline_mni = "{}/{}/alignment/baseline_mni/".format(_get_output(mse_bl),mse_bl)
    mni_angulated = "{}/{}/alignment/mni_angulated/".format(_get_output(mse_bl),mse_bl)
    if not os.path.exists(baseline_mni) and os.path.exists("{}/{}/alignment/".format(_get_output(mse_bl),mse_bl)):
        os.mkdir(baseline_mni)
    if not os.path.exists(bl_t1_mni + bl_t1_mni.split('/')[-1].replace('trans',"T1mni")) and os.path.exists("{}/{}/alignment/".format(_get_output(mse_bl),mse_bl)):
         if os.path.exists(mni_angulated):
            for item in os.listdir(mni_angulated):

                if item.endswith(".nii.gz") and not "flirt" in item:
                    new_name = item.replace("trans", "T1mni")
                    shutil.copyfile(mni_angulated +"/"+ item, baseline_mni +"/"+ new_name)


def get_series(mse):
    t1 = t2 = gad = bl_t1_mni = flair = affines = lst = "none"
    align = "{}/{}/alignment/status.json".format(_get_output(mse), mse)
    if os.path.exists(align):
        with open(align) as data_file:
            data = json.load(data_file)
            if len(data["t1_files"]) > 0:
                t1 = data["t1_files"][-1]
            if len(data["t2_files"]) > 0:
                t2 = data["t2_files"][-1]
            if len(data["gad_files"]) > 0:
                gad = data["gad_files"][-1]
            if len(data["flair_files"]) > 0:
                flair = data["flair_files"][-1]
            if len(data["affines"]) > 0:
                affines = data["affines"]
    lst_mask = glob(_get_output(mse) + "/{0}/mindcontrol/ms*{0}*FLAIR*/lst/lst_edits/no_FP_filled_FN*.nii.gz".format(mse))
    lst_mask2 = glob("{}/{}/lst/lpa/ples_lpa_m*index*.nii.gz".format(_get_output(mse),mse))
    if len(lst_mask) > 0:
        lst = lst_mask[0]
    elif len(lst_mask2) > 0:
        lst = lst_mask2[-1]

    return [t1, t2, flair, gad, affines, lst]

def get_mni_angulated(bl_t1,mse_bl):
    t1 = bl_t1.split("/")[-1].replace(".nii", "_trans.nii")
    bl_t1_mni = "{}/{}/alignment/mni_angulated/{}".format(_get_output(mse_bl),mse_bl,t1)
    if not os.path.exists(bl_t1_mni):
        print(mse_bl, "need to run align")
        cmd = ["pbr", mse_bl, "-w", "nifti","align","-R"]
        #Popen(cmd).wait()
    return bl_t1_mni

def create_affine(in_file, bl_t1_mni, mse):
    mni_affine = "{}/{}/alignment/mni_affine.mat".format(_get_output(mse), mse)
    out_file = "{}/{}/alignment/baseline_mni/{}".format(_get_output(mse),mse,in_file.split('/')[-1].replace(".nii", "_T1mni.nii"))
    if in_file.endswith(".nii.gz") and not "brain_mask" in in_file:
        #if not os.path.exists(os.path.split(in_file)[0]+"/mni_affine.mat"):
        bl_mni =  "{}/{}/alignment/baseline_mni/".format(_get_output(mse),mse)
        if not os.path.exists(bl_mni): os.mkdir(bl_mni)
        cmd = ["flirt", "-in", in_file, "-ref", bl_t1_mni,"-omat", mni_affine, "-dof", "6", "-out", out_file,"-cost","mutualinfo"]
        print("IMPORTANT COMAND")
        print(cmd)
        Popen(cmd).wait()
    return mni_affine


def flirt_reg(in_file, ref_file, mat, out):
    cmd = ["flirt", "-in", in_file, "-ref", ref_file, "-applyxfm", "-init", mat, "-out", out]
    print(cmd)
    Popen(cmd).wait()



def register_masks_MNI(lst_edit_sienax, bl_t1_mni, config, msid):
    les_mni = gm_mni = wm_mni = lesion_bin= ""
    mni_long = config["long_output_directory"] +'/'+ str(msid) + "/MNI/"
    if not os.path.exists(mni_long):os.mkdir(mni_long)
    for mse in os.listdir(lst_edit_sienax):
        lst_edit_sienax = lst_edit_sienax +'/'+ mse
        lesion = lst_edit_sienax + '/lesion_mask.nii.gz'
        mni_affine = "{}/{}/alignment/mni_affine.mat".format(_get_output(mse), mse)
        wm = lst_edit_sienax + '/I_stdmaskbrain_pve_2.nii.gz'
        gm = lst_edit_sienax + '/I_stdmaskbrain_pve_1.nii.gz'
        les_mni = mni_long + "lesion_" + mse + ".nii.gz"
        wm_mni  =  mni_long + "wm_" + mse + ".nii.gz"
        gm_mni  = mni_long + "gm_" + mse + ".nii.gz"
        if os.path.exists(lesion):
            flirt_reg(lesion, bl_t1_mni, mni_affine, les_mni )
            lesion_bin = lesion.replace(".nii","_bin.nii")
            cmd = ["fslmaths", lesion, "-bin",lesion_bin]
            Popen(cmd).wait()
        if os.path.exists(wm):
            flirt_reg(wm, bl_t1_mni, mni_affine, wm_mni)
            cmd = ["fslmaths", wm_mni, "-bin",wm_mni]
            Popen(cmd).wait()
        if os.path.exists(gm):
            flirt_reg(gm, bl_t1_mni, mni_affine, gm_mni )
            cmd = ["fslmaths", gm_mni, "-bin",gm_mni]
            Popen(cmd).wait()
    return [les_mni, wm_mni, gm_mni, lesion_bin]


def register_non_chop(mse, in_file, config):
    if in_file.endswith(".nii.gz"):
        nifti = in_file.replace("alignment", "nii").replace("_T1mni", "")
        mni_affine = os.path.split(in_file)[0] + "/mni_affine.mat"
        reorient = config["working_directory"] + mse + "_reorient.nii.gz"
        if not os.path.exists(config["working_directory"] + mse):
            os.mkdir(config["working_directory"] + mse)
        bl_nochop = "{}/{}/alignment/baseline_mni/no_chop/".format(_get_output(mse),mse)
        fullstd = bl_nochop + in_file.split("/")[-1].replace(".nii.gz","_fullstd.mat")

        if not "brain_mask" in in_file:
            if not os.path.exists(fullstd.replace("fullstd.mat","_nochop.nii.gz")):
                cmd = ["fslreorient2std", nifti, reorient]
                Popen(cmd).wait()

                cmd = ["flirt", "-in", reorient,"-ref", in_file.replace("_T1mni", ""), "-dof", "6","-omat", fullstd.replace("fullstd","_chop")]
                Popen(cmd).wait()

                cmd = ["convert_xfm", "-omat", fullstd,"-concat", mni_affine,fullstd.replace("fullstd","_chop")]
                print(cmd)
                Popen(cmd).wait()

                cmd = ["convert_xfm", "-omat", fullstd,"-concat", config["chop"],fullstd]
                print(cmd)
                Popen(cmd).wait()

                flirt_reg(reorient, config["mni_paddy"], fullstd, fullstd.replace("fullstd.mat","_nochop.nii.gz") )

def apply_tp2_flirt(in_file,bl_t1_mni,mse):
    mni_affine = "{}/{}/alignment/mni_affine.mat".format(_get_output(mse), mse)
    if os.path.exists(in_file) and not os.path.exists(in_file.replace(".nii", "_T1mni.nii")):
        bl_mni =  "{}/{}/alignment/baseline_mni/".format(_get_output(mse),mse)
        if not os.path.exists(bl_mni): os.mkdir(bl_mni)
        out_file = "{}/{}/alignment/baseline_mni/{}".format(_get_output(mse),mse,in_file.split('/')[-1].replace(".nii", "_T1mni.nii"))
        flirt_reg(in_file, bl_t1_mni, mni_affine, out_file)
    #return out_file

def create_mat_T1tp2_T1MNI(in_file, bl_t1_mni):
    cmd = ["flirt", "-dof", "6", "-in",  in_file.replace("_T1mni", ""), "-ref", bl_t1_mni, "-omat", os.path.split(in_file)[0] + "/mni_affine.mat"]
    print(cmd)
    Popen(cmd).wait()


def run_bias_corr(in_file, mse):
    bias_out = "{}/{}/N4corr/".format(_get_output(mse),mse)
    if not os.path.exists(bias_out):os.mkdir(bias_out)
    n4 = bias_out + in_file.split('/')[-1].replace(".nii.gz", "_n4corr.nii.gz")
    print("N4", n4)
    if not os.path.exists(n4):
        cmd = ["N4BiasFieldCorrection", "-d", "3", "-i", in_file,"-o", n4]
        print("N4BiasFieldCorrection", "-d", "3", "-i", in_file, "-o", n4)
        Popen(cmd).wait()
    return n4

def get_nawm(wm_MNI, flair_file, wm_eroded, base_dir):
    cmd = ["fslmaths", wm_MNI, "-ero", "-thr", ".1", "-mul",flair_file, wm_eroded]
    print(cmd)
    Popen(cmd).wait()

    cmd = ["bet",flair_file, base_dir + "/skull.nii.gz", "-s"]
    Popen(cmd).wait()

def cal_median(file):
    median = 0.0
    cmd = ["fslstats", file, "-P", "50"]
    proc = Popen(cmd, stdout=PIPE)
    try:
        output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0]
        median = float(output[0])
    except:
        pass
    return median

def create_ero_wm(wm_MNI, flair_file,wm_eroded, new_median_nawm, base_dir):
    cmd = ["fslmaths", wm_MNI, "-ero", "-thr", ".1", "-mul",flair_file, wm_eroded]
    Popen(cmd).wait()

    cmd = ["fslmaths",  wm_eroded, "-uthr", str(new_median_nawm), base_dir+"/ero_WM_Lhalf.nii.gz"]
    Popen(cmd).wait()


def dil_lesion_minus_gm(lesion_bin_MNI, gm_mni, lesion_dil):
    cmd = ["fslmaths",lesion_bin_MNI , "-dilM",  "-sub", gm_mni,"-thr", ".1","-bin", lesion_dil]
    Popen(cmd, stdout=PIPE).wait()

def create_wm_with_les(lesion_dil, wm_MNI, wm_with_les,file, wm_flair):
    cmd = ["fslmaths", lesion_dil, "-add", wm_MNI, "-bin", wm_with_les]
    print(cmd)
    Popen(cmd).wait()

    cmd = ["fslmaths", wm_with_les, "-mul",file, wm_flair]
    Popen(cmd).wait()

    return wm_with_les

def get_std(file):
    cmd = ["fslstats", file , "-S"]
    proc = Popen(cmd, stdout=PIPE)
    std_nawm = float([l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0])
    est_std = float(std_nawm) * 1.608
    return std_nawm

def get_vol(file):
    cmd = ["fslstats", file, "-V"]
    print(cmd)
    proc = Popen(cmd, stdout=PIPE)
    vol = float([l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0])
    return vol


def cal_hist(std, vol, wm_flair, median, file):
    std_times2 = std*std*2
    if std_times2 == 0:
        std_times2 = 0.00001
    part1 = vol/(math.sqrt(std_times2*(math.pi)))

    cmd = ["fslmaths", wm_flair, "-sub",str(median),"-sqr", "-div", str(std_times2), "-mul", "-1", "-exp", "-mul", str(part1), file]
    print(cmd)
    Popen(cmd).wait()


def les_mul_file(lesion_bin_MNI, flair_file, lesion_mul_flair, new_median_lesion, base_dir, median_nawm):
    cmd = ["fslmaths", base_dir + "/skull.nii.gz", "-uthr",str(median_nawm),"-bin",base_dir+ "/thr.nii.gz"]
    Popen(cmd).wait()

    cmd = ["fslmaths", lesion_bin_MNI,"-sub",base_dir + "/thr.nii.gz","-thr", ".1", "-bin", "-mul",flair_file,  lesion_mul_flair]
    Popen(cmd).wait()

    cmd = ["fslmaths", lesion_bin_MNI,"-thr", ".1", "-bin", "-mul",flair_file,  lesion_mul_flair]
    Popen(cmd).wait()

    cmd = ["fslmaths",  lesion_mul_flair, "-thr", str(new_median_lesion), base_dir+ "/lesion_Uhalf.nii.gz"]
    Popen(cmd).wait()
    print("FINISHED WITH LES MUL FILE")

def make_prob_map(gm_mni, base_dir, wm_MNI, no_wm, lesion_dil, wm_no_bs, wm_with_les, prob_map):
    cmd = ["fslmaths", gm_mni, "-dilM","-dilM", base_dir + "/gm_dil.nii.gz"]
    Popen(cmd).wait()

    cmd = ["fslmaths",wm_MNI, "-sub", no_wm, "-thr", ".1","-ero","-add",lesion_dil,"-bin", wm_no_bs] # can try adding back later "-sub",gm_mni,
    Popen(cmd).wait()

    cmd = ["fslmaths", base_dir+"/lesion_hist.nii.gz", "-add", base_dir+ "/wm_hist.nii.gz",base_dir+"/add_his.nii.gz"]
    Popen(cmd).wait()

    cmd = ["fslmaths",base_dir +"/lesion_hist.nii.gz", "-div",base_dir+ "/add_his.nii.gz","-mul", wm_with_les, prob_map]
    Popen(cmd).wait()

def create_les(lesion_dil, prob_map,wm_with_les, base_dir, gm_mni, final_lesion, wm_no_bs, prob_map_nobs,lesion_MNI):
    print("create les")
    cmd = ["fslmaths",lesion_dil,"-mul",prob_map, "-thr", ".99","-bin","-mul",wm_with_les,"-bin", "-sub",base_dir+ "/thr.nii.gz","-sub", gm_mni, "-thr", ".1", "-bin", final_lesion]
    print(cmd)
    Popen(cmd).wait()

    cmd = ["fslmaths",wm_no_bs, "-mul", prob_map, "-ero","-ero", prob_map_nobs]
    Popen(cmd).wait()

    cmd = ["fslmaths", prob_map_nobs,"-thr", ".99","-sub",base_dir+ "/thr.nii.gz","-thr", ".1", "-bin", "-add", final_lesion, "-bin", base_dir+ "/lesion_prob_map.nii.gz"]
    Popen(cmd).wait()

    cmd = ["fslmaths", lesion_MNI, "-dilM", "-mul", base_dir+ "/lesion_prob_map.nii.gz", base_dir+ "/lesion_labeled.nii.gz" ]
    Popen(cmd).wait()

def create_t2_les(wm_with_les, lesion_dil, prob_map, wm_eroded, final_lesion, lesion_MNI, base_dir):
    print("create t2 les")
    cmd = ["fslmaths", wm_with_les, "-ero","-ero", wm_with_les]
    print(cmd)
    Popen(cmd).wait()

    cmd = ["fslmaths",lesion_dil,"-mul",prob_map, "-thr", ".99","-bin","-mul",wm_eroded,"-bin", final_lesion]
    Popen(cmd).wait()

    cmd = ["fslmaths", lesion_MNI, "-dilM", "-mul", final_lesion, base_dir+ "/lesion_labeled.nii.gz" ]
    Popen(cmd).wait()


def reg_les_origspace(mse, final_lesion,t1_file, out_file):
    affine = glob(_get_output(mse)+ "/{0}/alignment/mni_affine.mat".format(mse))[0]
    inverse_aff = affine.replace(".mat", "_inv.mat")
    if not os.path.exists(_get_output(mse)+'/'+ mse+ out_file): #_get_output(mse)+'/'+ mse+"/lesion_origspace_flair") or not :
        os.mkdir(_get_output(mse)+'/'+ mse+ out_file)
    les_origspace = _get_output(mse)+'/'+ mse+ out_file+ "/lesion.nii.gz"

    cmd = ["convert_xfm", "-omat", inverse_aff, "-inverse", affine]
    Popen(cmd, stdout=PIPE).wait()

    cmd = ["flirt", "-applyxfm","-init",inverse_aff,"-in",final_lesion,"-ref",t1_file, "-out", les_origspace]
    print(cmd)
    Popen(cmd, stdout=PIPE).wait()


def create_flair_lesions(msid, mse, t1, flair, wm_mni, gm_mni,lesion,lesion_bin, config):
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    print("T1", t1)
    print("FLAIR", flair)
    print("WM MNI", wm_mni)
    print("GM MNI", gm_mni)
    print("LESION", lesion)

    base_dir = config["working_directory"] +"/"+mse + "/lesion_mni/"
    mni_long = config["long_output_directory"] +"/"+ msid + "/MNI/"
    flair_file = run_bias_corr(flair, mse)
    wm_eroded = base_dir + "/wm_eroded.nii.gz"
    wm_flair = base_dir + "/wm_flair.nii.gz"

    wm_with_les = base_dir+ "/wm_withles.nii.gz"
    lesion_dil = base_dir + "/lesion_dil.nii.gz"
    lesion_mul_flair = base_dir + "/lesion.nii.gz"
    prob_map = base_dir +"/prob_map_new.nii.gz"
    prob_map_nobs = base_dir +"/prob_map_nowmbs.nii.gz"
    final_lesion = base_dir + "/lesion_final_new.nii.gz"
    wm_no_bs = base_dir+ "/wm_no_bs.nii.gz"

    if os.path.exists(flair_file):
        if not os.path.exists(config["working_directory"] +"/"+mse):os.mkdir(config["working_directory"] +"/"+mse)
        if not os.path.exists(base_dir):os.mkdir(base_dir)

        flair_lesion = "{0}/{1}/lesion_origspace_flair/lesion.nii.gz*".format(_get_output(mse), mse )
        #if not os.path.exists(flair_lesion):

        cmd = ["fslmaths", lesion, "-bin", lesion_bin]
        Popen(cmd).wait()

        get_nawm(wm_mni, flair_file, wm_eroded, base_dir)
        median_nawm = cal_median(wm_eroded)
        new_median_nawm = median_nawm - .000001
        create_ero_wm(wm_mni, flair_file,wm_eroded, new_median_nawm, base_dir)
        dil_lesion_minus_gm(lesion_bin, gm_mni, lesion_dil)

        create_wm_with_les(lesion_dil, wm_mni, wm_with_les, flair_file, wm_flair)
        std_nawm = get_std(base_dir+ "/ero_WM_Lhalf.nii.gz")

        vol_nawm = get_vol(wm_eroded)
        cal_hist(std_nawm, vol_nawm , wm_flair, median_nawm, base_dir+"/wm_hist.nii.gz")


        cmd = ["fslmaths", lesion_bin,"-thr", ".1", "-bin", "-mul",flair_file,  lesion_mul_flair]
        print("fslmaths", lesion_bin,"-thr", ".1", "-bin", "-mul",flair_file,  lesion_mul_flair)
        Popen(cmd).wait()
        median_lesion = cal_median(lesion_mul_flair)
        new_median_lesion = median_lesion + .000001
        print(new_median_lesion)


        les_mul_file(lesion_bin, flair_file, lesion_mul_flair, new_median_lesion, base_dir, median_nawm)
        std_lesion = get_std(base_dir +"/lesion_Uhalf.nii.gz")
        print(std_lesion)
        vol_lesion = get_vol(lesion_mul_flair)
        print(vol_lesion)
        print("***")
        if not vol_lesion == 0.0:

            cal_hist(std_lesion, vol_lesion, wm_flair, median_lesion,base_dir+"/lesion_hist.nii.gz")
            make_prob_map(gm_mni, base_dir, wm_mni, no_wm, lesion_dil, wm_no_bs, wm_with_les, prob_map)
            create_les(lesion_dil, prob_map,wm_with_les, base_dir, gm_mni, final_lesion, wm_no_bs, prob_map_nobs,lesion)
            reg_les_origspace(mse, final_lesion, t1, "/lesion_origspace_flair/")

            new_les = "{}/{}/new_lesion/lesion.nii.gz".format(_get_output(mse), mse)

            if os.path.exists(new_les):
                #shutil.rmtree(new_les)
                shutil.move(new_les, "/data/henry6/gina/s_test/"+ mse+"_new_les.nii.gz")
            submit("pbr " +mse + " -w sienax_optibet -R")

no_wm = "/data/henry6/PBR/surfaces/MNI152_T1_1mm/mri/no_wm_MNI_new.nii.gz"

def create_t2_lesions(msid, mse, t1, t2, wm_mni, gm_mni,lesion,lesion_bin, config):
    base_dir = config["working_directory"] +"/"+mse + "/lesion_mni_t2/"
    mni_long = config["long_output_directory"] +"/"+ msid + "/MNI/"

    #lesion = str(glob(mni_long + "lesion_mse*.nii.gz")[0])
    wm_eroded = base_dir + "/wm_eroded"
    wm_t2 = base_dir + "/wm_t2.nii.gz"

    wm_with_les = base_dir+ "/wm_withles.nii.gz"
    lesion_dil = base_dir + "/lesion_dil.nii.gz"
    lesion_mul_t2 = base_dir + "/lesion.nii.gz"
    prob_map = base_dir +"/prob_map_new.nii.gz"
    final_lesion = base_dir + "/lesion_final_new.nii.gz"
    wm_no_bs = base_dir+ "/wm_no_bs.nii.gz"

    if os.path.exists(t2):

        t2_lesion = "{0}/{1}/lesion_origspace_t2/lesion.nii.gz*".format(_get_output(mse), mse )
        #if not os.path.exists(t2_lesion):
        if not os.path.exists(config["working_directory"] +"/"+mse): os.mkdir(config["working_directory"] +"/"+mse)
        if not os.path.exists(base_dir):os.mkdir(base_dir)


        if not os.path.exists(_get_output(mse) +"/"+mse + "/lesion_mni_t2/"):
            os.mkdir(_get_output(mse) +"/"+mse + "/lesion_mni_t2/")

        cmd = ["fslmaths", lesion, "-bin", lesion_bin]
        Popen(cmd).wait()
        print("RUNNING BIAS CORR")
        t2_file = run_bias_corr(t2, mse)
        get_nawm(wm_mni, t2_file, wm_eroded, base_dir)
        median_nawm = cal_median(wm_eroded)
        new_median_nawm = median_nawm - .000001
        create_ero_wm(wm_mni, t2_file,wm_eroded, new_median_nawm, base_dir)
        dil_lesion_minus_gm(lesion_bin, gm_mni, lesion_dil)
        create_wm_with_les(lesion_dil, wm_mni, wm_with_les,t2_file, wm_t2)
        std_nawm = get_std(base_dir + "/ero_WM_Lhalf.nii.gz")
        vol_nawm = get_vol(wm_eroded)
        cal_hist(std_nawm, vol_nawm, wm_t2, median_nawm, base_dir + "/wm_hist.nii.gz")


        median_lesion = cal_median(lesion_mul_t2)
        new_median_lesion = median_lesion - .000001
        les_mul_file(lesion_bin, t2_file, lesion_mul_t2, new_median_lesion, base_dir, median_nawm)
        std_lesion = get_std(base_dir +"/lesion_Uhalf.nii.gz")
        vol_lesion = get_vol(lesion_mul_t2)


        if not vol_lesion == 0.0:
            cal_hist(std_lesion, vol_lesion, wm_t2, median_lesion,base_dir+"/lesion_hist.nii.gz")
            make_prob_map(gm_mni, base_dir, wm_mni, no_wm, lesion_dil, wm_no_bs, wm_with_les, prob_map)


            create_t2_les(wm_with_les, lesion_dil, prob_map, wm_eroded, final_lesion, lesion, base_dir)

            reg_les_origspace(mse, final_lesion, t1, "/lesion_origspace_t2/")

            new_les = "{}/{}/new_lesion/lesion.nii.gz".format(_get_output(mse), mse)

            if os.path.exists(new_les):
                shutil.move(new_les, "/data/henry6/gina/s_test/"+ mse+"_new_les.nii.gz")
                #shutil.rmtree(new_les)
            cmd = ["pbr", mse, "-w", "sienax_optibet","-R"]
            #Popen(cmd).wait()
            submit("pbr " +mse + " -w sienax_optibet -R")


def run_lst_sienax(msid, config,mse):
    lst = mse_lst = ""
    lst_edit_sienax = config["long_output_directory"] +"/"+ msid + "/lst_edit_sienax/"
    if os.path.exists(lst_edit_sienax):
        for mse_lst in os.listdir(lst_edit_sienax):
            print("**************", mse_lst)
            if mse_lst.startswith("mse"):
                lst_mask = glob("{0}/{1}/mindcontrol/ms*{1}*FLAIR*/lst/lst_edits/no_FP_filled_FN*.nii.gz".format(_get_output(mse), mse_lst))
                lst_mask2 = glob("{}/{}/lst/lpa/ples_lpa_m*index*.nii.gz".format(_get_output(mse_lst),mse_lst))
                if len(lst_mask)>0:
                     lst =lst_mask[-1]
                elif len(lst_mask2)>0:
                    lst =lst_mask2[-1]
    else:
        L = get_lst(msid)
        lst = L[0]
        mse_lst = L[1]
        if os.path.exists(lst):
            if not os.path.exists(config["long_output_directory"] +"/"+ msid):os.mkdir(config["long_output_directory"] +"/"+ msid)
            if not os.path.exists(lst_edit_sienax):os.mkdir(lst_edit_sienax)
        if mse_lst.startswith("mse"):
            t1 = get_series(mse_lst)[0]
            cmd = ["sienax_optibet", t1, "-lm", lst, "-r","-d","-o", lst_edit_sienax + mse_lst]
            print(cmd)
            Popen(cmd).wait()
    return [lst_edit_sienax, mse_lst]

def get_lst(msid):
    lst = mse = ""
    lst_mask = glob("/data/henry*/PBR/subjects/mse*/mindcontrol/{}*FLAIR*/lst/lst_edits/no_FP_filled_FN*.nii.gz".format(msid))
    #lst_mask2 = glob("/data/henry*/PBR/subjects/mse*/lst/lpa/ples_lpa_m*index*.nii.gz".format(_get_output(mse),mse))
    if len(lst_mask) > 0:
        lst = lst_mask[-1]
        mse = lst.split('/')[5]
        print("^^^^^^^^^^^^^^", lst, mse)
    return [lst,mse]


def align_to_baseline(msid, mse_bl, mse):
    bl_t1 = get_series(mse_bl)[0]
    print(bl_t1)
    bl_t1_mni = get_mni_angulated(bl_t1, mse_bl)
    copy_mni_bl(bl_t1_mni, mse_bl)
    if mse.startswith("mse")and len(mse) > 3:
        t1 = get_series(mse)[0].replace("reorient","").replace("N4corr","").replace("_brain_mask","")
        t2 = get_series(mse)[1]
        flair = get_series(mse)[2]
        gad = get_series(mse)[3]

        lst_edit = run_lst_sienax(msid, config,mse)
        lst_edit_sienax= lst_edit[0]
        mse_lst = lst_edit[1]
        print(lst_edit)
        print(lst_edit_sienax)
        print(mse_lst)

    if mse_lst.startswith("mse")and len(mse_lst) > 3:
        t1_lst = get_series(mse_lst)[0]
        print(t1_lst)
        create_affine(t1_lst, bl_t1_mni,mse_lst)

    #register everything to baseline T1 MNI space - creating /alignment/baseline_mni directories
    print("create affine")
    create_affine(t1,bl_t1_mni,mse)
    files = [t1, t2, flair, gad]
    for file in files:
        register_non_chop(mse, file, config)
        if not mse == mse_bl:
            print("apply tp2 flirt")
            apply_tp2_flirt(file, bl_t1_mni,mse)


    #lst_edit_sienax = run_lst_sienax(msid, lst, config)
    #lst_mse = lst.split('/')[5]
    if os.path.exists(lst_edit_sienax) and mse_lst.startswith("mse") and mse.startswith("mse"):

        masks = register_masks_MNI(lst_edit_sienax, bl_t1_mni, config, msid)
        lesion = masks[0]
        wm_mni = masks[1]
        gm_mni = masks[2]
        lesion_bin = masks[3]
        flair = "{}/{}/alignment/baseline_mni/{}".format(_get_output(mse),mse,flair.split('/')[-1].replace(".nii", "_T1mni.nii"))
        t1_mni =  "{}/{}/alignment/baseline_mni/{}".format(_get_output(mse),mse,t1.split('/')[-1].replace(".nii", "_T1mni.nii"))
        t2 = "{}/{}/alignment/baseline_mni/{}".format(_get_output(mse),mse,t2.split('/')[-1].replace(".nii", "_T1mni.nii"))
        if not flair.endswith("none") and len(t1) >1:
            print("FLAIR ^^^^^^^^^^^^^^^^^^^^^^^^^^^", msid, mse, t1, flair, wm_mni, gm_mni,lesion,lesion_bin)
            create_flair_lesions(msid, mse, t1, flair, wm_mni, gm_mni,lesion,lesion_bin, config)
        elif len(t2) > 5 and len(t1) >1:
            print("T2 ^^^^^^^^^^^^^^^^^^^^^^", msid, mse, t1, t2, wm_mni, gm_mni,lesion, lesion_bin)
            create_t2_lesions(msid, mse, t1, t2, wm_mni, gm_mni,lesion, lesion_bin, config)
        else:
            print(mse, "CAN NOT MAKE LESION MASK")




def run_dicom(mse):
    try:
        #cmd = ["pbr", mse, "-w", "dicom", "-rps", password,"-R" ]
        cmd = ["ms_dcm_qr2", "-t", mse.replace("mse", ""), "-e", working + mse, "-p", password]
        print(cmd)
        Popen(cmd).wait()
    except:
        pass

def get_dicom(mse):
    try:
        dicom = glob(working + "/{0}/E*".format(mse))[0]
        print("DICOM DIRECTORY:", dicom)
    except:
        run_dicom(mse)
        try:
            glob(working + "/{0}/E*".format(mse))[0]
            print(mse, "Successfully retrieved dicom from mspacman")
        except:
            print(mse, "Error retrieving dicom from mspacman, need to investigate further")
            with open(mspac_path + "/dicom.txt", "a") as text_file:
                text_file.write(mse + "\n")
            pass
        pass


def get_modality(mse):
    num = mse.split("mse")[-1]
    print("ms_dcm_exam_info", "-t", num, "-D")
    cmd = ["ms_dcm_exam_info", "-t", num, "-D"]
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
                print(sequence_name, " is the {0}".format(sq))
            except:
                print(mse, "No {0} in dicom identified by the heuristic...Please check sequnces and heuristic".format(sq))
                pass
        if len(sequence_name) > 1:
            print("checking for sequence names in nifti and align folders")
            try:
                check_for_sq_names(mse, sq, "/nii/", sequence_name)
                check_for_sq_names(mse, sq, "/alignment/", sequence_name)
            except:
                pass
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
        pass


def run_align(mse):
    try:
        cmd = ["pbr", mse, "-w", "align", "-R"]
        print(cmd)
        Popen(cmd).wait()
    except:
        pass


def check_in_nii_align(sq, x, mse, data, pipeline, sequence_name):
    if not sequence_name.startswith("ms"):
        check_nondeid(mse)
    if pipeline == "/nii/":

        if str(sequence_name) not in str(data[x]):
            print("No {0} in nifti status file, but {1} in dicom heuristic... re-running nifti conversion".format(sequence_name, sq))
            run_nifti(mse)
        else:
            print("THE {0} FILE EXISTS... ready to run align".format(sq))

        if "_reorient" in str(data[x]):
            run_nifti(mse)

    if pipeline == "/alignment/":
        if str(sequence_name) not in str(data[x]):
            print("No {0} in align status file, but {1} in dicom heuristic... re-running alignment".format(sequence_name, sq))
            run_align(mse)
        else:
            print("THE {0} FILE EXISTS...".format(sq))

        if "_reorient" in str(data[x]):
            run_align(mse)


def check_for_sq_names(mse, sq, pipeline, sequence_name ):
    nifti_align = pbr_dir(mse) +  pipeline + "/status.json"
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
    nifti = pbr_dir(mse) + "/nii/status.json"
    if not os.path.exists(nifti):
        run_nifti(mse)
    else:
        print(mse, "NIFTI HAS BEEN SUCCESSFULLY RUN")
        #check_nondeid(mse)


def get_align(mse):
    align =pbr_dir(mse) +"/alignment/status.json"
    if not os.path.exists(align):
        print("ALIGN DIRECTORY DOES NOT EXIST")
        run_align(mse)
    else:
        print(mse, "ALIGN HAS BEEN SUCCESSFULLY RUN", align)

def write_dicom_log(mse):
    dicom = ""
    try:
        dicom = glob(working + "/{0}/E*".format(mse))[0]
        print(dicom)
    except:
        with open(mspac_path+ "/dicom.txt", "a") as text_file:
            text_file.write(mse + "\n")
            print("no dicom for ", mse, "---writing dicom log")
    return dicom

def check_nii_localheur(mse):
    if os.path.exists(pbr_dir(mse) + '/nii/heuristic.json'):
        print("removing subject heuristic....",pbr_dir(mse) + '/nii/heuristic.json' )
        os.remove(pbr_dir(mse)+ '/nii/heuristic.json')
        run_nifti(mse)


def check_nondeid(mse):
    with open(mspac_path + "/not_deidentified.txt", "a") as text_file:
        text_file.write(mse + "\n")


def pbr_dir(mse):
    pbr = _get_output(mse) + '/' + mse + '/'
    return pbr

def run_first(mse):
    first = _get_output(mse) + '/'+ mse + "/first_all"
    if not os.path.exists(first):
        submit("pbr " +mse + " -w first_all -R")

def check_pbr(mse):
    print("running...", mse)
    get_dicom(mse)
    write_dicom_log(mse)

    if len(write_dicom_log(mse)) > 1:

        check_nii_localheur(mse)
        get_modality(mse)

        if not os.path.exists(pbr_dir(mse) + "/nii/status.json"):
            with open(mspac_path + "/nifti.txt", "a") as text_file:
                text_file.write(mse + "\n")
        if not os.path.exists(pbr_dir(mse) + "/alignment/status.json"):
            with open(mspac_path + "/align.txt", "a") as text_file:
                text_file.write(mse + "\n")


def run_siena(msid,mse_bl,mse):
    if not os.path.exists("/data/henry10/PBR_long/subjects/"+msid+ "/siena_optibet/"+ mse_bl +"__" + mse +"/report.siena"):
        submit("pbr " +mse_bl +" "+ mse+ " -w siena_optibet -R")

def run_all(c):
    df = pd.read_csv("{}".format(c))
    for idx in range(len(df)):
        msid = df.loc[idx, 'msid']
        mse = df.loc[idx, 'mse']
        mse_bl = df.loc[idx, "mse_bl"]
        check_pbr(mse)
        check_pbr(mse_bl)
        run_first(mse)
        t1 = ""

        align = "{}/{}/alignment/status.json".format(_get_output(mse), mse)
        if os.path.exists(align):
            with open(align) as data_file:
                data = json.load(data_file)
                if len(data["t1_files"]) > 0:
                    t1 = data["t1_files"][-1].split('/')[-1].replace(".nii.gz","")

        sienax_path = "{}/{}/sienax_optibet/{}/lesion_mask.nii.gz".format(_get_output(mse),mse,t1)
        if not os.path.exists(sienax_path):
            align_to_baseline(msid, mse_bl, mse)
            submit("pbr " +mse + " -w sienax_optibet -R")
        run_siena(msid, mse_bl, mse)



if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code allows you to grab the mse, scanner, birthdate, sex  given a csv (with date and msid)')
    parser.add_argument('-i', help = 'csv containing the msid and date')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    run_all(c)



