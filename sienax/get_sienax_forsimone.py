from subprocess import check_output, check_call
from getpass import getpass
import nibabel as nib
import numpy as np
from glob import glob
import csv
import os
import pbr
from pbr.base import _get_output

#password = getpass("mspacman password: ")
#check_call(["ms_dcm_echo", "-p", password])

folders = sorted(glob("ms*"))

writer = open("/home/sf522915/sienax_data_Simone.csv", "w")
spreadsheet = csv.DictWriter(writer, 
                             fieldnames=["msid", "Scan Date",
                                        "vscale", 
                                        "brain vol (u, mm3)",
                                        "WM vol (u, mm3)", 
                                        "GM vol (u, mm3)",
                                        "vCSF vol (u, mm3)",
                                        "cortical vol (u, mm3)",
                                        "lesion vol (u, mm3)", "mseID"])
spreadsheet.writeheader()


mse_list = [ "4997", "6788",  "5000", "9013",  "5003", "3624",  "3703", "6939",\
             "5008", "7847",  "5011", "8773",  "3985", "7130",  "5400", "7164",\
            "5264", "6881",  "7860", "11645", "4994", "3051","4854", "6794",\
            "5134", "7390",  "5257", "8602",  "6701", "10154", "6719", "7730",\
             "5007", "4258"]


for mse in mse_list:
    mse = "mse" + mse
    if os.path.exists(_get_output(mse) + '/' + mse + "/sienax_flair/"):
        path = _get_output(mse) + '/' + mse + "/nii/"
        first_file = next(os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)))
        msid = os.path.split(first_file)[1].split("-")[0]
        print(msid)
        
        
        row = {"msid": msid, "mseID": mse}
        """check_call(["ms_dcm_echo", "-p", password])
        output = check_output(["ms_get_phi", "--examID", mse, "--studyDate", "-p", password])
        output = [output.decode('utf8')]
        for line in output:
            if "StudyDate" in line:
                row["Scan Date"] = line.split()[-1]"""

        report = os.path.join(_get_output(mse), mse, "sienax_flair/report.sienax")
        with open(report, "r") as f:
            lines = [line.strip() for line in f.readlines()]
            for line in lines:
                if not len(line) >= 1:
                    continue
                if line.startswith("VSCALING"):
                    row["vscale"] = line.split()[1]
                elif line.startswith("pgrey"):
                    row["cortical vol (u, mm3)"] = line.split()[2]
                elif line.startswith("vcsf"):
                    row["vCSF vol (u, mm3)"] = line.split()[2]
                elif line.startswith("GREY"):
                    row["GM vol (u, mm3)"] = line.split()[2]
                elif line.startswith("WHITE"):
                    row["WM vol (u, mm3)"] = line.split()[2]
                elif line.startswith("BRAIN"):
                    row["brain vol (u, mm3)"] = line.split()[2]

        lm = os.path.join(_get_output(mse), mse, "sienax_flair/lesion_mask.nii.gz")
        img = nib.load(lm)
        data = img.get_data()
        row["lesion vol (u, mm3)"] = np.sum(data)

        spreadsheet.writerow(row)

writer.close()

