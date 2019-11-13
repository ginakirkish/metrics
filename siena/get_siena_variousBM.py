from glob import glob
import pandas as pd
import numpy as np
import csv
import os
from subprocess import Popen, PIPE
from pbr.base import _get_output
import json
import nibabel as nib
import argparse
pbr_long = "/data/henry12/siena_BM/"

def get_pbvc(siena_long, df, idx):
    pbvc = ""
    if len(siena_long) > 0:
        siena_report = siena_long[0] + '/report.siena'
        print(siena_report, "THIS IS THE SIENA REPORT")
        if os.path.exists(siena_report):
            with open(siena_report, "r") as f:
                lines = [line.strip() for line in f.readlines()]
                for line in lines:
                    if line.startswith("finalPBVC"):
                        pbvc =  line.split()[1]
                        print(pbvc)
                        #df.loc[idx,"{}".format(siena_long)] = pbvc
        #if os.path.exists(siena_long[0] + ''):
    return pbvc

def get_t1(mse):
    with open('{0}/{1}/alignment/status.json'.format(_get_output(mse), mse)) as data_file:
        data = json.load(data_file)
        if len(data["t1_files"]) > 0:
            t1_file = data["t1_files"][-1]
            print(t1_file)
        return t1_file

def get_hdr(t1_mse2):
    cmd = ["fslhd", t1_mse2]
    proc = Popen(cmd, stdout=PIPE)
    output = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]]
    dim1, dim2, dim3 = "0", "0", "0"
    for items in output[5:6]:
        print(items[0], items[1])
        dim1 = items[1]
    for items in output[6:7]:
        print(items[0], items[1])
        dim2 = items[1]
    for items in output[7:8]:
        print(items[0], items[1])
        dim3 = items[1]
    total_dim = {"x" : int(dim1), "y": int(dim2), "z": int(dim3)}
    print("DIMENSIONS:", total_dim)
    return total_dim


if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code allows you to grab siena values given a csv (with mse and msid) and an output csv')
    parser.add_argument('-i', help = 'csv containing the msid and mse')
    parser.add_argument('-o', help = 'output csv for siena data')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    out = args.o
    print(c, out)
    ind = 0
    baseline_msid, mse_baseline, mse2 = ["","",""]
    df = pd.read_csv('{0}'.format(c))
    for idx in range (len(df)):
        msid = df.loc[idx,'msid']
        msid = "ms" + msid.replace("ms", "").lstrip("0")
        mse = df.loc[idx,'mse']
        if msid == baseline_msid:
            x = 0
            ind = ind+1
            #print(ind, msid, mse)
        else:
            baseline_msid = msid
            ind = 0
        if ind == 0 :
            mse1 =  df.loc[idx,'mse']
        if not mse1 == mse:
            mse2 = mse
            print(msid, mse1, mse2)
            #get_siena(c, out)
            siena_bet = glob("/{0}/{1}/siena_fromBL_BET/{2}_{3}".format(pbr_long, msid, mse1, mse2))
            siena_optibet = glob("/{0}/{1}/siena_fromBL_optiBET/{2}_{3}".format(pbr_long, msid, mse1, mse2))
            siena_optibet_ANTs = glob('/{0}/{1}/siena_ANTsBM_fromBL/{2}_{3}'.format(pbr_long, msid, mse1, mse2))
            siena_optibet_nrigid = glob('/{0}/{1}/siena_NrigidBM_fromBL/{2}_{3}'.format(pbr_long, msid, mse1, mse2))
            siena_monstr = glob('/{0}/{1}/siena_MONSTR/{2}_{3}'.format(pbr_long, msid, mse1, mse2))
            siena_warp = glob('/{0}/{1}/siena_fnirtBM_fromBL/{2}_{3}'.format(pbr_long, msid, mse1, mse2))
            siena_optibet2 = glob("/data/henry10/PBR_long/subjects/{0}/siena_optibet/{1}_{2}".format(msid, mse1, mse2))
            all_siena = [siena_bet, siena_optibet, siena_optibet_ANTs, siena_optibet_nrigid, siena_monstr, siena_warp, siena_optibet2]
            #all_siena = [siena_monstr]
            for siena_long in all_siena:
                if len(siena_long) > 0:
                    print(siena_long)
                    print("SIENA LABEL",siena_long[0].split('/')[-2])
                    df.loc[idx,"{}".format(siena_long[0].split('/')[-2])] = get_pbvc(siena_long, df, idx)
                    print(get_pbvc(siena_long, df, idx))

                df.loc[idx, 'MSID'] = "ms" +msid.replace("ms","").lstrip("0")

                t1_mse1 = get_t1(mse1)
                t1_mse2 = get_t1(mse2)
                get_hdr(t1_mse2)
                size_mse1 = get_hdr(t1_mse1)
                size_mse2 = get_hdr(t1_mse2)
                df.loc[idx,'dim_mse1_x'] = size_mse1["x"]
                df.loc[idx,'dim_mse1_y'] = size_mse1["y"]
                df.loc[idx,'dim_mse1_z'] = size_mse1["z"]
                df.loc[idx,'dim_mse2_x'] = size_mse2["x"]
                df.loc[idx,'dim_mse2_y'] = size_mse2["y"]
                df.loc[idx,'dim_mse2_z'] = size_mse2["z"]
                df.loc[idx, 'nrigid report'] =  ('/{0}/{1}/siena_NrigidBM_fromBL/{2}_{3}/report.html'.format(pbr_long, msid, mse1, mse2))
                df.loc[idx, "msid"] = msid
                df.loc[idx, "mse1"] = mse1
                df.loc[idx, "mse2"] = mse2
                df.to_csv('{0}'.format(out))