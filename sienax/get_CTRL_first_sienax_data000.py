import os
import pandas as pd
from subprocess import Popen, PIPE
from glob import glob

df = pd.read_csv("/home/sf522915/Documents/ctrl_mse.csv")



for idx in range(len(df)):
    mse = df.loc[idx, 'mse']
    msid = df.loc[idx, 'msID']


    try:

        first = glob(str('/data/henry6/antje/C1A/CTRL_nifti/{0}/*/first/'.format(msid)))[0]
        print(first)
    except:
        first = ""
        pass

    if os.path.exists(first):
        for files in os.listdir(first):
            if files.endswith("all_none_firstseg.nii.gz"):
                print(files)
                seg = first+ files

                cmd = ["fslstats",seg,"-l", "9.5", "-u","10.5", "-V"]
                proc = Popen(cmd, stdout=PIPE)
                lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0]
                #print(lines)
                df.loc[idx,"L Thalamus"] = lines

                cmd = ["fslstats",seg,"-l", "10.5", "-u","11.5", "-V"]
                proc = Popen(cmd, stdout=PIPE)
                lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0]
                df.loc[idx,"L Caudate"] = lines
                #print(lines)


                cmd = ["fslstats",seg,"-l", "11.5", "-u","12.5", "-V"]
                proc = Popen(cmd, stdout=PIPE)
                lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0]
                df.loc[idx,"L Putamen"] = lines
                #print(lines)


                cmd = ["fslstats",seg,"-l", "48.5", "-u","49.5", "-V"]
                proc = Popen(cmd, stdout=PIPE)
                lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0]
                df.loc[idx,"R Thalamus"] = lines
                #print(lines)


                cmd = ["fslstats",seg,"-l", "49.5", "-u","50.5", "-V"]
                proc = Popen(cmd, stdout=PIPE)
                lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0]
                df.loc[idx,"R Caudate"] = lines
                #print(lines)


                cmd = ["fslstats",seg,"-l", "50.5", "-u","51.5", "-V"]
                proc = Popen(cmd, stdout=PIPE)
                lines = [l.decode("utf-8").split() for l in proc.stdout.readlines()[:]][0][0]
                df.loc[idx,"R Putamen"] = lines
                #print(lines)


    try:
        sienax = glob('/data/henry6/antje/C1A/CTRL_nifti/{0}/*/sienax_optibet/'.format(msid))[0]
        print(sienax)
    except:
        sienax = ""
        pass

    if os.path.exists(sienax): 
        with open(sienax + '/report.sienax', "r") as f:
            lines = [line.strip() for line in f.readlines()]
            for line in lines:
                if not len(line) >= 1:
                    continue
                if line.startswith("VSCALING"):
                    df.loc[idx, "vscale origT1"] = line.split()[1]
                    print(mse,"vscale new origT1",line.split()[1])
                elif line.startswith("pgrey"):
                    df.loc[idx,"cortical vol (u, mm3) origT1"] =line.split()[2]
                    print(line.split()[2])
                elif line.startswith("vcsf"):
                    df.loc[idx,"vCSF vol (u, mm3) origT1"] = line.split()[2]
                    print(line.split()[2])

                elif line.startswith("GREY"):
                    df.loc[idx,"GM vol (u, mm3) origT1"] = line.split()[2]
                    print(line.split()[2])

                elif line.startswith("WHITE"):
                    df.loc[idx,"WM vol (u, mm3) origT1"] = line.split()[2]
                    print(line.split()[2])

                elif line.startswith("BRAIN"):
                   df.loc[idx,"brain vol (u, mm3) origT1"] = line.split()[2]
                   print(line.split()[2])

        df.to_csv("/home/sf522915/Documents/CTRL_sienax_first_new0000.csv")
