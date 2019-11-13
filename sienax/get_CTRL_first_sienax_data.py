import os
import pandas as pd
from subprocess import Popen, PIPE
from glob import glob

df = pd.read_csv("/home/sf522915/Documents/ctrl_mse.csv")

def _get_output(mse):
    mse_num = int(mse[3:])
    if mse_num <= 4500:
        output_dir = '/data/henry7/PBR/subjects/'
    else:
        output_dir = '/data/henry11/PBR/subjects/'
    return output_dir


for idx in range(len(df)):

    try:


        mse = df.loc[idx, 'mse']
        #mse = "mse" + str(mse).split("mse")[1].lstrip("0")
        print(mse)

        cmd = ["ms_get_phi", "--examID", mse, "-p", "Rosie1313"]
        print(cmd)
        proc = Popen(cmd, stdout=PIPE)
        output = str([l.decode("utf-8").split() for l in proc.stdout.readlines()[:]])
    except:
        pass
    """try:

        if "Sex" in output:
            if 'F' in output:
                sex = "Female"
            elif 'M' in output:
                sex = "Male"
            else:
                sex ="Unknown"
            print(sex)
            df.loc[idx, "Sex"] = sex
        birth = output.split("PatientBirthDate")[1].split("=")[1].split("StudyTime")[0].replace("'","").replace(",","").replace("[","").replace("]","")
        print(birth)
        df.loc[idx, "birthdate"] = birth

        scan_date = output.split("StudyDate")[1].split("=")[1].replace("'","").replace(",","").replace("[","").replace("]","")
        print("scan date", scan_date)
        df.loc[idx, "ScanDate"] = scan_date

    except:
        pass"""

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
    sienax = ""
    try:
        sienax = glob(str(_get_output(mse) + '/' + mse + '/sienax_optibet/ms*/report.sienax'))[0]
    except: 
        sienax = _get_output(mse) +'/' + mse + '/sienax_optibet/report.sienax'
        pass

    if os.path.exists(sienax): 
        with open(sienax, "r") as f:
            lines = [line.strip() for line in f.readlines()]
            for line in lines:
                if not len(line) >= 1:
                    continue
                if line.startswith("VSCALING"):
                    df.loc[idx, "vscale origT1"] = line.split()[1]
                    print(mse,"vscale new origT1",line.split()[1])
                elif line.startswith("pgrey"):
                    df.loc[idx,"cortical vol (u, mm3) origT1"] =line.split()[2]
                elif line.startswith("vcsf"):
                    df.loc[idx,"vCSF vol (u, mm3) origT1"] = line.split()[2]
                elif line.startswith("GREY"):
                    df.loc[idx,"GM vol (u, mm3) origT1"] = line.split()[2]
                elif line.startswith("WHITE"):
                    df.loc[idx,"WM vol (u, mm3) origT1"] = line.split()[2]
                elif line.startswith("BRAIN"):
                   df.loc[idx,"brain vol (u, mm3) origT1"] = line.split()[2]
        df.to_csv("/home/sf522915/Documents/CTRL_sienax_first_new2.csv")
