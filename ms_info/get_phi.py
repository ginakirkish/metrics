
import argparse
import pandas as pd
import subprocess
from subprocess import check_call
from getpass import getpass



password = getpass("mspacman password: ")
check_call(["ms_dcm_echo", "-p", password])


def get_phi(c, out):
    df = pd.read_csv("{}".format(c))
    for idx in range (len(df)):
        mse = df.loc[idx, "mse"]
        msid = df.loc[idx, "msid"]
        print(msid, mse)
        proc = subprocess.Popen(["ms_get_phi", "--examID", mse, "-p",password],stdout=subprocess.PIPE)
        for line in proc.stdout:
            line = str(line.rstrip())

            if "PatientBirthDate" in   line:
                birth =   line.split()[-1].lstrip("b'").rstrip("'")
                print("BIRTH", birth)
                df.loc[idx,"BirthDate"] = birth
            if "PatientSex" in   line:
                sex=   line.split()[-1].lstrip("b'").rstrip("'")
                print("SEX", sex)
                df.loc[idx,"Sex"] = sex
            if "StudyDate" in   line:
                date=   line.split()[-1].lstrip("b'").rstrip("'")
                print("Date", date)
                df.loc[idx,"StudyDate"] = date
            if "StationName" in line:
                scanner= line.split()[-1].lstrip("b'").rstrip("'")
                print("Scanner", scanner)
                df.loc[idx,"Scanner"] = scanner
            df.to_csv("{}".format(out))

if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code allows you to grab phi values given a csv (with mse and msid) and an output csv')
    parser.add_argument('-i', help = 'csv containing the msid and mse')
    parser.add_argument('-o', help = 'output csv for siena data')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    out = args.o
    print(c, out)
    get_phi(c, out)