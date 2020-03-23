import csv, json, sys
import os
from pbr.base import _get_output
import argparse
import pandas as pd
from pandas.io.json import json_normalize



def get_siena_data(msid, mse_bl, mse):

    henry10 = "/data/henry10/PBR_long/subjects/" + msid + '/siena_optibet/'
    siena_label = final_pbvc = ""
    if os.path.exists(henry10):
        for mse_siena in os.listdir(henry10):
            if str(mse_siena).startswith(str(mse_bl)) and str(mse_siena).endswith(str(mse)):
                siena_report = os.path.join(henry10, mse_siena, "report.siena")
                if os.path.exists(siena_report):
                    print(siena_report)
                    siena_label = "True"
                    with open(siena_report, "r") as f:
                        lines = [line.strip() for line in f.readlines()]
                        for line in lines:
                            if line.startswith("finalPBVC"):
                                final_pbvc =  line.split()[1]


    return [final_pbvc, siena_label]


def  write_csv(c, out):
    df = pd.read_csv("{}".format(c))
    for idx in range(len(df)):
        msid = df.loc[idx, 'msid']
        mse = df.loc[idx, 'mse']
        mse_bl = df.loc[idx, "mse_bl"]
        print(msid, mse)
        df.loc[idx, 'mse'] = mse

        metrics = "{}/{}/metrics.json".format(_get_output(mse), mse)
        if os.path.exists(metrics):
            print(metrics)
            with open(metrics) as data_file:
                data = json.load(data_file)
                #try:
                if os.path.exists(metrics):
                    if len(data["SIENAX"])>0:
                        sienax = data['SIENAX']
                        for items in sienax:
                            header = items.keys()
                            for h in header:
                                print(h)
                                print(items[h])
                                df.loc[idx, h ] = items[h]
                    try:
                        if len(data["First"])>0:
                            first = data["First"]
                            for items in first:
                                header = items.keys()
                                for h in header:
                                    print(h)
                                    print(items[h])
                                    df.loc[idx, h ] = items[h]
                    except:
                        pass

                    if len(data["SIENA"])>0:
                        siena = data["SIENA"]
                        for items in siena:
                            header = items.keys()
                            for h in header:
                                print(h)
                                print(items[h])
                                df.loc[idx, h ] = items[h]

                    if len(data["Sequences"])>0:
                        seq = data["Sequences"]
                        for items in seq:
                            header = items.keys()
                            for h in header:
                                print(h)
                                print(items[h])
                                df.loc[idx, h ] = items[h]

                    if len(data["Scanner_Info"])>0:
                        scan_info = data["Scanner_Info"]
                        for items in scan_info:
                            header = items.keys()
                            for h in header:
                                print(h)
                                print(items[h])
                                df.loc[idx, h ] = items[h]
                    try:

                        if len(data["freesurfer"])>0:
                            FS = data["freesurfer"]
                            for items in FS:
                                header = items.keys()
                                for h in header:
                                    print(h)
                                    print(items[h])
                                    df.loc[idx, h  + "(FS)"] = items[h]
                    except:
                        pass

                    """listy = [sienax, first, seq, scan_info, FS]
                    for pipe in listy:
                        for items in pipe:

                            header = items.keys()
                            for h in header:
                                print(h)
                                print(items[h])
                                df.loc[idx, h ] = items[h]"""
                #except:
                    #pass
        pbvc = get_siena_data(msid, mse_bl, mse)
        df.loc[idx, "PBVC"] = pbvc[0]

    df.to_csv(out)



if __name__ == '__main__':
    parser = argparse.ArgumentParser('This code allows you to grab the mse, scanner, birthdate, sex  given a csv (with date and msid)')
    parser.add_argument('-i', help = 'csv containing the msid and date')
    parser.add_argument('-o', help = 'output csv for siena data')
    parser.add_argument
    args = parser.parse_args()
    c = args.i
    out = args.o
    print(c, out)
    write_csv(c, out)
