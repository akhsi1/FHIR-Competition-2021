"""Builds the dataset, compiles all solutions, creates test files, and zips test files."""
import argparse, os, sys
import subprocess
import zipfile
from solutions.build_soln import main as compile_soln
from paramiko import SSHClient
from secret_keys import JUDGE_IP

parser = argparse.ArgumentParser()
parser.add_argument("--no-dataset", action="store_false", dest="dataset")
parser.add_argument("--no-upload", action="store_false", dest="upload")
parser.add_argument("-o", "--override", type=str, default="")

GRADING_FOLDERS = ["Q1", "Q2", "Q3", "Q4", "Q7"]
PROBLEM_NAMES = {
    "Q1": "datatest",
    "Q2": "bionic",
    "Q3": "patientlinks", 
    "Q4": "batchtesting", 
    "Q5": "extraweight", 
    "Q6": "intertest",
    "Q7": "sample",
}

def main():
    global GRADING_FOLDERS
    args = parser.parse_args(sys.argv[1:])

    if args.override:
        GRADING_FOLDERS = [args.override]
    
    if args.dataset:
        from dataset_generator.source import main as generate_data
        print("GENERATING DATA...")
        generate_data()
        if args.upload:
            print("UPLOADING DATA...")
            ssh = SSHClient()
            ssh.load_system_host_keys()
            ssh.connect(JUDGE_IP, username="ubuntu")
            ssh.exec_command("rm -r problems/data/dataset")
            ssh.exec_command("mkdir problems/data/dataset")
            for sub in ["encounters", "observations", "organizations", "patients", "practitioners"]:
                ssh.exec_command(f"mkdir problems/data/dataset/{sub}")
                for f in os.listdir(f"dataset/build/{sub}"):
                    subprocess.run(f"scp dataset/build/{sub}/{f} ubuntu@{JUDGE_IP}:/home/ubuntu/problems/data/dataset/{sub}/{f}".split())

    for f in os.listdir("solutions"):
        f_p = os.path.join("solutions", f)
        if os.path.isdir(f_p) and f.startswith("Q"):
            print("Compiling", f)
            for f2 in os.listdir(f_p):
                if f2.endswith(".py") and "compiled" not in f2 and "solution" in f2:
                    # Compile solution
                    compile_soln(os.path.join(f_p, f2))
            # Generate test data
            if os.path.exists(os.path.join(f_p, "test_generator.py")):
                subprocess.run(f"python -m solutions.{f}.test_generator".split())
            if f in GRADING_FOLDERS:
                for x in range(1, 4):
                    if os.path.exists(f"solutions/{f}/{x}.in"):
                        with open(f"solutions/{f}/{x}.in", "r") as test_in:
                            with open(f"solutions/{f}/{x}.out", "w") as test_out:
                                subprocess.run(f"python -m solutions.{f}.solution_compiled".split(), stdin=test_in, stdout=test_out)
            if args.upload:
                # Archive.
                with zipfile.ZipFile(f"solutions/{f}/archive.zip", "w") as z:
                    for x in range(1, 4):
                        if os.path.exists(f"solutions/{f}/{x}.in"):
                            z.write(f"solutions/{f}/{x}.in", arcname=f"{x}.in")
                        if os.path.exists(f"solutions/{f}/{x}.out"):
                            z.write(f"solutions/{f}/{x}.out", arcname=f"{x}.out")
                # SCP
                subprocess.run(f"scp solutions/{f}/grader.py ubuntu@{JUDGE_IP}:/home/ubuntu/problems/{PROBLEM_NAMES[f]}/grader.py".split())
                subprocess.run(f"scp solutions/{f}/archive.zip ubuntu@{JUDGE_IP}:/home/ubuntu/problems/{PROBLEM_NAMES[f]}/archive.zip".split())
                for x in range(1, 4):
                    if os.path.exists(f"solutions/{f}/{x}.in"):
                        subprocess.run(f"scp solutions/{f}/{x}.in ubuntu@{JUDGE_IP}:/home/ubuntu/problems/{PROBLEM_NAMES[f]}/{x}.in".split())
                    if os.path.exists(f"solutions/{f}/{x}.out"):
                        subprocess.run(f"scp solutions/{f}/{x}.out ubuntu@{JUDGE_IP}:/home/ubuntu/problems/{PROBLEM_NAMES[f]}/{x}.out".split())
                # Remove archive.
                os.remove(f"solutions/{f}/archive.zip")

if __name__ == "__main__":
    main()
