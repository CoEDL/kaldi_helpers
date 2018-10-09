from src.json_to_kaldi import *


def test_json_to_kaldi1():
    
    input_json = os.path.join(".", "test", "testfiles", "example.json")
    output_dir = os.path.join(".", "data")
    command = ["python", "src\\json_to_kaldi.py",
               "--input_json", f"{input_json}",
               "--output_folder", f"{output_dir}"
               "--silence_markers"]
    command = subprocess.list2cmdline(command)
    os.system(command)

    required_files = {"corpus.txt", "segments", "spk2gender", "text", "utt2spk", "wav.scp"}
    for folder in os.listdir(output_dir):
        files_present = set(os.listdir(os.path.join(output_dir, folder)))
        assert len(required_files) <= len(files_present)
        assert required_files.issubset(files_present)


def test_json_to_kaldi2():
    input_json = os.path.join(".", "test", "testfiles", "does_not_exist.json")
    output_dir = os.path.join(".", "data")
    command = ["python", "src\\json_to_kaldi.py",
               "--input_json", f"{input_json}",
               "--output_folder", f"{output_dir}"
                                  "--silence_markers"]
    command = subprocess.list2cmdline(command)
    os.system(command)

    result: subprocess.CompletedProcess = subprocess.run(command, check=True)
    assert result.returncode != 0