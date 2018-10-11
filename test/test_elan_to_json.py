from src.elan_to_json import *

SCRIPT_PATH = os.path.join('.', 'src', 'elan_to_json.py')


def test_process_eaf():

    # Using script to extract data from test .eaf files
    input_dir = os.path.join("resources", "corpora", "abui_toy_corpus", "data")
    output_dir = os.path.join('.', "test", "testfiles")
    output_json = os.path.join(output_dir, "dirty.json")
    command = ["python", SCRIPT_PATH,
               "--input_dir", input_dir,
               "--output_dir", output_dir,
               "--output_json", output_json]
    result: subprocess.CompletedProcess = subprocess.run(command, check=True)
    assert result.returncode == 0

    with open(output_json) as f:
        contents: List[Dict[str, Union[str, float]]] = json.loads(f.read())
    os.remove(output_json)

    # Manual extraction of transcription data from test .eaf files
    all_files_in_directory: Set[str] = set(glob.glob(os.path.join(input_dir, "*.eaf"),
                                                     recursive=True))
    utterances: List[Dict[str, Union[str, float]]] = []
    for file_name in all_files_in_directory:
        utterances = utterances + process_eaf(file_name, "Phrase")

    assert len(utterances) == len(contents)
    for dictionary in utterances:
        assert dictionary in contents
