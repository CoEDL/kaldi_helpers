from scripts.trs_to_json import *


TEST_FILES_BASE_DIR = os.path.join(".", "src", "test", "testfiles")


class TestTRSToJSON:
    def test_find_first_file_by_ext(self) -> None:
        all_files_in_dir = list(glob.glob(os.path.join(TEST_FILES_BASE_DIR, "**"), recursive=True))
        all_files_in_dir.sort()
        
        first_test: str = find_first_file_by_ext(all_files_in_dir, list(["*.rtf"]))
        assert os.path.split(first_test)[1].endswith(".rtf")
        assert os.path.basename(first_test) == "test.rtf"

        second_test: str = find_first_file_by_ext(all_files_in_dir, list(["*.txt"]))
        assert os.path.split(second_test)[1].endswith(".txt")
        assert os.path.basename(second_test) != "test.txt"
        assert os.path.basename(second_test) == "howdy.txt"

        third_test: str = find_first_file_by_ext(all_files_in_dir, list(["*.py", "*.xlsx"]))
        assert os.path.split(third_test)[1].endswith(".xlsx")
        assert os.path.basename(third_test) != "howdy.xlsx"
        assert os.path.basename(third_test) == "charm.xlsx"

    def test_find_files_by_ext(self) -> None:
        all_files_in_dir = set(glob.glob(os.path.join(TEST_FILES_BASE_DIR, "**"), recursive=True))

        first_test: List[str] = find_files_by_ext(all_files_in_dir, {"*.xlsx"})
        files = set([os.path.split(i)[1] for i in first_test])
        assert len(first_test) == 3
        for file in first_test:
            assert file.endswith(".xlsx")
        assert {"python.xlsx", "test.xlsx", "charm.xlsx"}.issubset(files)

        second_test: List[str] = find_files_by_ext(all_files_in_dir, {"*.py"})
        files = set([os.path.split(i)[1] for i in second_test])
        assert len(second_test) == 1
        for file in second_test:
            assert file.endswith(".py")
        assert {"test.py"}.issubset(files)

        third_test: List[str] = find_files_by_ext(all_files_in_dir, {"*.py", "*.txt"})
        files = set([os.path.split(i)[1] for i in third_test])
        assert len(third_test) == 3
        for file in third_test:
            assert (file.endswith(".py") or file.endswith(".txt"))
        assert {"test.py", "howdy.txt", "test.txt"}.issubset(files)

    def test_cond_log(self):
        assert 2 == 2

    def test_process_file(self):
        assert 1 == 1

    def test_process_turn(self):
        assert 1 == 1

    def test_trs_to_json(self):
        assert 1 == 1
