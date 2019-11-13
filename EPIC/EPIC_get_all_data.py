

import csv
import os
import pbr
from pbr.base import _get_output
import pandas as pd
import argparse
import json
import numpy as np
from subprocess import Popen, PIPE




def get_align(mse):
    align = _get_output(mse)+"/"+mse+"/alignment/status.json"
    return align


def run_siena(c,  out):

    df = pd.read_csv("{}".format(c))
    for idx in range(len(df)):
        msid = df.loc[idx, 'msid']
        mse = df.loc[idx, 'mse']
        siena_long = "/data/henry10/PBR_long/subjects/" + msid + '/siena_optibet/'
        if os.path.exists(siena_long):
            for mse_siena in os.listdir(siena_long):
                if mse_siena.startswith(mse):
                    df.loc[idx, 'siena_optibet'] = mse_siena
                    siena_report = os.path.join(siena_long, mse_siena, "report.siena")
                    if not os.path.exists(siena_report):
                        continue
                    with open(siena_report, "r") as f:
                        lines = [line.strip() for line in f.readlines()]
                        for line in lines:
                            if line.startswith("finalPBVC"):
                                df.loc[idx, 'PBVC'] = line.split()[1]

        first = df.loc[idx, "L Thalamus"]
        print(first)
        if str(first) == "0": 

        
            if os.path.exists(_get_output(mse) +"/"+ mse + "/first/"):
                print(_get_output(mse) +"/"+ mse + "/first/")
                for files in os.listdir(_get_output(mse) + "/" +mse +"/first/"):
                    if files.endswith("firstseg.nii.gz"):
                        print(files)
                        seg = _get_output(mse) + "/" +mse +"/first/"+ files

                        cmd = ["fslstats",seg,"-l", "9.5", "-u","10.5", "-V"]
                        proc = Popen(cmd, stdout=PIPE)
                        lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0]
                        df.loc[idx, "L Thalamus"] = lines

                        cmd = ["fslstats",seg,"-l", "10.5", "-u","11.5", "-V"]
                        proc = Popen(cmd, stdout=PIPE)
                        lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0]
                        df.loc[idx, "L Caudate"] = lines

                        cmd = ["fslstats",seg,"-l", "11.5", "-u","12.5", "-V"]
                        proc = Popen(cmd, stdout=PIPE)
                        lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0]
                        df.loc[idx,"L Putamen"] = lines

                        cmd = ["fslstats",seg,"-l", "48.5", "-u","49.5", "-V"]
                        proc = Popen(cmd, stdout=PIPE)
                        lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0]
                        df.loc[idx,"R Thalamus"] = lines

                        cmd = ["fslstats",seg,"-l", "49.5", "-u","50.5", "-V"]
                        proc = Popen(cmd, stdout=PIPE)
                        lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0]
                        df.loc[idx,"R Caudate"] = lines

                        cmd = ["fslstats",seg,"-l", "50.5", "-u","51.5", "-V"]
                        proc = Popen(cmd, stdout=PIPE)
                        lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0]
                        df.loc[idx,"R Putamen"] = lines
    print(df)
    df.to_csv("{0}".format(out))


if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code allows you to grab siena values given a csv (with mse and msid) and an output csv')
    parser.add_argument('-i', help = 'csv containing the msid and mse')
    parser.add_argument('-o', help = 'output csv for siena data')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    out = args.o
    print(c, out)
    run_siena(c, out)
