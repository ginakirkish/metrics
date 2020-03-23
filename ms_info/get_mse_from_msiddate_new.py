import numpy as np
import os
#import pbr
from subprocess import Popen, PIPE
import pandas as pd
import argparse
import csv
from subprocess import check_output, check_call
from getpass import getpass
import pandas as pd


password = getpass("mspacman password: ")
check_call(["ms_dcm_echo", "-p", password])



def get_mse(c, out):
    print("running...")

    df = pd.read_csv("{}".format(c))

    df.columns.values[1:62]

    for idx in range(len(df)):
        msid = "ms" + df.loc[idx, 'msid'].replace("ms","").lstrip("0")
        mse = df.loc[idx, "mse"]
        #date1 = ""
        if not str(mse).startswith("mse"):
            date1 = str(df.loc[idx, 'date'])
            cmd = ["ms_get_patient_imaging_exams", "--patient_id", msid.split("ms")[1].lstrip("0"), "--dcm_dates"]
            proc = Popen(cmd, stdout=PIPE)
            lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[5:]]
            tmp = pd.DataFrame(lines, columns=["mse", "date"])
            tmp["msid"] = msid
            mse = tmp["mse"]
            print(mse)
            for _, row in tmp.iterrows():
                mse = row["mse"]
                date2 = str(row["date"]).split(".0")[0]
                if str(date1) == (date2):
                    print(date1, date2, mse)
                    df.loc[idx, "mse"] = "mse"+ mse.zfill(4)
        #except:
            #pass


    
            print(date1, msid)
            out = "{}".format(out)
            df.to_csv(out)  


if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code allows you to grab the mse, scanner, birthdate, sex  given a csv (with date and msid)')
    parser.add_argument('-i', help = 'csv containing the msid and date')
    parser.add_argument('-o', help = 'output csv')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    out = args.o
    print(c, out)
    get_mse(c, out)
