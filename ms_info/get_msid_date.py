from subprocess import check_call, Popen, PIPE, check_output
from time import time
import argparse
import json
import pbr
from pbr.base import _get_output
from glob import glob
import os
import shutil
import pandas as pd
from getpass import getpass


password = getpass("mspacman password: ")
check_call(["ms_dcm_echo", "-p", password])

def get_date(mse, o):
    if str(mse).startswith("mse"):
        output = check_output(["ms_get_phi", "--examID", mse.replace("mse",""), "--studyDate", "-p", password])
        output = [output.decode('utf8')]
        for line in output:
            if "StudyDate" in line:
                date = line.split()[-1]
                #print(date)
                df.loc[idx,"date"] = date
        output = check_output(["ms_get_patient_id", "--exam_id", mse.split("mse")[-1]])
        output = [output.decode('utf8')]
        for line in output:
            if "MS" in line:
                msid = line.split()[-1]
                df.loc[idx, "msid"] = msid
                print(msid)
    df.to_csv("{}".format(o))




if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', help = 'csv containing the msid and mse, need to be sorted by msid and date')
    parser.add_argument('-o', help ='output csv')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    o = args.o
    df = pd.read_csv("{}".format(c))
    for idx in range (len(df)):
        mse = df.loc[idx, "mse"]
        #msid = df.loc[idx, "msid"]
        #print(msid, mse)
        get_date(mse, o)