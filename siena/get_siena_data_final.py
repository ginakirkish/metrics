

import csv
import os
import pbr
from pbr.base import _get_output
import pandas as pd
import argparse
import json


def get_align(mse):
    align = _get_output(mse)+"/"+mse+"/alignment/status.json"
    return align


def run_siena(c,  out):
    writer = open("{}".format(out), "w")
    spreadsheet = csv.DictWriter(writer, fieldnames=["msid", "mseID",
                                                     "siena", "PBVC","T1_1", "T1_2"
                                                      ])
    spreadsheet.writeheader()



    df = pd.read_csv("{}".format(c))

    for _, row in df.iterrows():
        msid ="ms" + str(row['msid']).replace("ms", "").lstrip("0")
        siena_long = "/data/henry10/PBR_long/subjects/" + msid + '/siena_optibet/'
        mse =  str(row["mse"])
        print(msid, mse)
        row = {"msid": msid, "mseID": mse}

        if os.path.exists(siena_long):
            for mse_siena in os.listdir(siena_long):
                if mse_siena.startswith(mse):
                    row["siena"] = mse_siena
                    mse1 =  "mse" + mse_siena.split("mse")[1].split("_")[0]
                    mse2 = "mse" + mse_siena.split("mse")[2]
                    siena_report = os.path.join(siena_long, mse_siena, "report.siena")

                    if not os.path.exists(siena_report):
                        continue
                    with open(siena_report, "r") as f:
                        lines = [line.strip() for line in f.readlines()]
                        for line in lines:
                            if line.startswith("finalPBVC"):
                                row["PBVC"] =  line.split()[1]

                    if os.path.exists(get_align(mse1)):

                        with open(get_align(mse1)) as data_file:
                            data = json.load(data_file)
                        if len(data["t1_files"]) == 0:
                            continue
                        else:
                            t1_file = data["t1_files"][-1].split('/')[-1]
                            row["T1_1"] = t1_file

                    if os.path.exists(get_align(mse2)):
                        with open(get_align(mse2)) as data_file:
                            data = json.load(data_file)
                        if len(data["t1_files"]) == 0:
                            continue
                        else:
                            t1_file2 = data["t1_files"][-1].split('/')[-1]
                            row["T1_2"] = t1_file2


        spreadsheet.writerow(row)

    writer.close()

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



