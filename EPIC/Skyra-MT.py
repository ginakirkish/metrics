import argparse

import json
import pandas as pd
import pbr
from pbr.base import _get_output
import os
from glob import glob


def get_mt(mse):
    mt_ON, mt_OFF, mt_t1 = "","",""
    nii = "{}/{}/nii/status.json".format(_get_output(mse), mse)
    if os.path.exists(nii):
        with open(nii) as data_file:
            data = json.load(data_file)
            if len(data["mt_files"])>0:
                mt = data["mt_files"][0]
                for lines in mt:
                    if "NON_MT_TR11_FL15" in lines:
                        mt_t1 = lines
                    elif "NON_MT" in lines:
                        mt_OFF = lines
                    else:
                        mt_ON = lines
    return mt_ON, mt_OFF, mt_t1


def get_t2_les(mse):
    t2_les_path = glob("{}/{}/lesion_origspace*/lesion.nii.gz".format(_get_output(mse),mse))
    if len(t2_les_path)>0:
        t2_les = t2_les_path[0]
    else:
        t2_les = ""
    return t2_les

def get_wm(mse):
    wm_path = glob("{}/{}/sienax_optibet/ms*/I_stdmaskbrain_seg_2.nii.gz".format(_get_output(mse),mse))
    wm_path2 = glob("{}/{}/sienaxorig_*/I_stdmaskbrain_seg_2.nii.gz".format(_get_output(mse),mse))
    if len(wm_path)>0:
        wm = wm_path[0]
    elif len(wm_path2)>0:
        wm = wm_path2[-1]
    else:
        wm = ""
    return wm

def get_t1(mse):
    t1 = ""
    align = "{}/{}/alignment/status.json".format(_get_output(mse), mse)
    if os.path.exists(align):
        with open(align) as data_file:
            data = json.load(data_file)
            if len(data["t1_files"]) > 0:
                t1 = data["t1_files"][-1]
    return t1


def make_csv(c,out):
    df = pd.read_csv("{}".format(c))


    for idx in range(len(df)):
        msid = df.loc[idx, 'msid']
        mse = df.loc[idx,'mse']
        df.loc[idx, "MT ON"] = get_mt(mse)[0]
        df.loc[idx, "MT OFF"] = get_mt(mse)[1]
        df.loc[idx, "MT T1"] = get_mt(mse)[2]
        df.loc[idx, "T1"] = get_t1(mse)
        df.loc[idx, "wm"] = get_wm(mse)
        df.loc[idx, "t2 les"] = get_t2_les(mse)
    df.to_csv("{0}".format(out))


if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code allows you to grab siena values given a csv (with mse and msid) and an output csv')
    parser.add_argument('-i', help = 'csv containing the msid and mse')
    parser.add_argument('-o', help = 'output csv')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    out = args.o
    make_csv(c,out)