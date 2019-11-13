from subprocess import check_output, check_call
from getpass import getpass
import nibabel as nib
import numpy as np
from glob import glob
import csv
import os

password = getpass("mspacman password: ")
#check_call(["ms_dcm_echo", "-p", password])

folders = sorted(glob("ms*"))

writer = open("/home/sf522915/sienax_data_pbr.csv", "w")
spreadsheet = csv.DictWriter(writer, 
                             fieldnames=["msid", "Scan Date", "Scan Status",
                                        "vscale", 
                                        "brain vol (u, mm3)",
                                        "WM vol (u, mm3)", 
                                        "GM vol (u, mm3)",
                                        "vCSF vol (u, mm3)",
                                        "cortical vol (u, mm3)",
                                        "lesion vol (u, mm3)", "mseID"])
spreadsheet.writeheader()

base_dir = "/data/henry7/PBR/subjects/"


for mse in os.listdir(base_dir):
    if os.path.exists(base_dir + mse + "/sienax_flair/"):
        path = base_dir + mse + "/nii/"
        first_file = next(os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)))
        msid = os.path.split(first_file)[1].split("-")[0]
        print(msid)
        
        
        row = {"msid": msid, "Scan Status": "Skyra", "mseID": mse}
        check_call(["ms_dcm_echo", "-p", password])
        output = check_output(["ms_get_phi", "--examID", mse, "--studyDate", "-p", password])
        output = [output.decode('utf8')]
        for line in output:
            if "StudyDate" in line:
                row["Scan Date"] = line.split()[-1]

        report = os.path.join(base_dir, mse, "sienax_flair/report.sienax")
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

        lm = os.path.join(base_dir, mse, "sienax_flair/lesion_mask.nii.gz")
        img = nib.load(lm)
        data = img.get_data()
        row["lesion vol (u, mm3)"] = np.sum(data)

        spreadsheet.writerow(row)

writer.close()
