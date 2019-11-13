import os
import pandas as pd
from subprocess import Popen, PIPE
from glob import glob
from subprocess import check_output, check_call
import json
import pandas as pd
import pbr
from pbr.base import _get_output
import argparse



def get_first(df, out):
    for idx in range (len(df)):
        msid = df.loc[idx,'msid']
        msid = "ms" + msid.replace("ms", "").lstrip("0")
        mse = df.loc[idx,'mse']
        mse = "mse" + mse.replace("mse", "").lstrip("0")


        if os.path.exists(_get_output(mse) +"/"+ mse + "/first/"):
            print(_get_output(mse) +"/"+ mse + "/first/")
            for files in os.listdir(_get_output(mse) + "/" +mse +"/first/"):
                if files.endswith("firstseg.nii.gz"):
                    print(files)
                    seg = _get_output(mse) + "/" +mse +"/first/"+ files

                    cmd = ["fslstats",seg,"-l", "9.5", "-u","10.5", "-V"]
                    proc = Popen(cmd, stdout=PIPE)
                    lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0]
                    df.loc[idx,"L Thalamus"] = lines

                    cmd = ["fslstats",seg,"-l", "10.5", "-u","11.5", "-V"]
                    proc = Popen(cmd, stdout=PIPE)
                    lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0]
                    df.loc[idx,"L Caudate"] = lines

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


                    df.to_csv("{}".format(out))


if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code allows you to grab the mse, scanner, birthdate, sex  given a csv (with date and msid)')
    parser.add_argument('-i', help = 'csv containing the msid and date')
    parser.add_argument('-o', help = 'output csv for siena data')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    out = args.o
    print(c, out)
    df = pd.read_csv("{}".format(c))
    get_first(df, out)