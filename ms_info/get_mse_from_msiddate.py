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

    writer = open("{}".format(out), "w")
    spreadsheet = csv.DictWriter(writer, fieldnames=[
                            "msID", "mseID", "ExamDate",
                            "PatientSex", "BirthDate", "scanner"])
    spreadsheet.writeheader()
    towrite = {}
    df = pd.read_csv("{}".format(c))
    for _, row in df.iterrows():
        msid = "ms" + str(row['msid']).replace("ms","").lstrip("0")
        date1 = str(row['date']).replace("-","")
        #date1 = date1.split('/')[2] + date1.split('/')[1].zfill(2) + date1.split('/')[0].zfill(2)  
        
        cmd = ["ms_get_patient_imaging_exams", "--patient_id", msid.split("ms")[1], "--dcm_dates"]
        proc = Popen(cmd, stdout=PIPE)
        lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[5:]]
        tmp = pd.DataFrame(lines, columns=["mse", "date"])
        tmp["msid"] = msid
        mse = tmp["mse"]
        #date2 = tmp["date"]
        print(msid, date1)
        for _, row in tmp.iterrows():
            mse = row["mse"]
            date2 = row["date"]
            if str(date1) == (date2):
                towrite = {}
                towrite["ExamDate"] = str(date1)
                towrite["msID"] = msid.zfill(4)
                towrite["mseID"] = "mse"+ mse.zfill(4)
                try:
                    check_call(["ms_dcm_echo", "-p", password])
                    output = check_output(["ms_get_phi", "--examID","mse"+ mse,  "-p", password])
                    output = [output.decode('utf8')]
                    print(output)

                    for line in output:
                        towrite["PatientSex"] = line.split("=")[10].split("Study")[0]
                        towrite["BirthDate"] = line.split("=")[6].split("Study")[0]
                        towrite["scanner"] = line.split("=")[1].split("Ref")[0]
                except:
                    pass

        print(date1, msid, mse)
        spreadsheet.writerow(towrite)
    writer.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code allows you to grab the mse, scanner, birthdate, sex  given a csv (with date and msid)')
    parser.add_argument('-i', help = 'csv containing the msid and date')
    parser.add_argument('-o', help = 'output csv for siena data')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    out = args.o
    print(c, out)
    get_mse(c, out)
