from src.json_to_kaldi import *

SCRIPT_PATH: str = os.path.join(".", "src", "json_to_kaldi.py")

def test_json_to_kaldi1():
    
    input_json: str = os.path.join(".", "test", "testfiles", "example.json")
    output_dir: str = os.path.join(".", "data")
    command: List[str] = ["python", f"{SCRIPT_PATH}",
               "--input_json", f"{input_json}",
               "--output_folder", f"{output_dir}"]
    command: str = subprocess.list2cmdline(command)
    os.system(command)

    required_files: Set[str] = {"corpus.txt", "segments", "spk2gender", "text", "utt2spk", "wav.scp"}
    for folder in os.listdir(output_dir):
        folder: str = os.path.join(output_dir, folder)
        if os.path.isdir(folder):
            files_present: Set[str] = set(os.listdir(folder))
            assert len(required_files) <= len(files_present)
            assert required_files.issubset(files_present)
    shutil.rmtree(output_dir)


def test_json_to_kaldi2():
    input_json = os.path.join(".", "test", "testfiles", "does_not_exist.json")
    output_dir = os.path.join(".", "data")
    command = ["python", f"{SCRIPT_PATH}",
               "--input_json", f"{input_json}",
               "--output_folder", f"{output_dir}"
                                  "--silence_markers"]
    command = subprocess.list2cmdline(command)

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while process.poll() is None:
        process.stdout.readline()  # give output_scripts from your execution/your own message
    command_result = process.wait()  # catch return code
    assert command_result != 0 # assert failure

