import os
import unittest

from pyprint.ConsolePrinter import ConsolePrinter
from coalib.output.printers.LogPrinter import LogPrinter
from coala_utils.ContextManagers import (
    simulate_console_inputs, suppress_stdout)
from coala_quickstart.generation.FileGlobs import get_project_files
from coala_quickstart.generation.Utilities import get_gitignore_glob
from coalib.collecting.Collectors import collect_files


class TestQuestion(unittest.TestCase):

    def setUp(self):
        self.printer = ConsolePrinter()
        self.log_printer = LogPrinter(self.printer)

    def test_get_project_files(self):
        orig_cwd = os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.makedirs("file_globs_testfiles", exist_ok=True)
        os.chdir("file_globs_testfiles")

        os.makedirs("src", exist_ok=True)
        os.makedirs("ignore_dir", exist_ok=True)
        open(os.path.join("src", "file.c"), "w").close()
        open("root.c", "w").close()
        open(os.path.join("ignore_dir", "src.c"), "w").close()
        open(os.path.join("ignore_dir", "src.js"), "w").close()

        with suppress_stdout(), simulate_console_inputs("ignore_dir/**"):
            res, _ = get_project_files(
                self.log_printer, self.printer, os.getcwd())
            self.assertIn(os.path.normcase(
                os.path.join(os.getcwd(), "src", "file.c")), res)
            self.assertIn(os.path.normcase(
                os.path.join(os.getcwd(), "root.c")), res)
            self.assertNotIn(os.path.normcase(
                os.path.join(os.getcwd(), "ignore_dir/src.c")), res)
            self.assertNotIn(os.path.normcase(
                os.path.join(os.getcwd(), "ignore_dir/src.js")), res)

        os.chdir(orig_cwd)

    def test_get_project_files_gitignore(self):
        orig_cwd = os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.makedirs("file_globs_gitignore_testfiles", exist_ok=True)
        os.chdir("file_globs_gitignore_testfiles")

        with open(".gitignore", "w") as f:
            f.write("""
# Start of gitignore
build
ignore.c
/tests
/upload.c
/*.py
*.pyc
__pycache__
# End of gitignore""")

        os.makedirs("another_folder", exist_ok=True)
        os.chdir("another_folder")
        with open('.gitignore', 'w') as f:
            f.write("""
# Start of gitignore
*.js
# End of gitignore""")
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.chdir("file_globs_gitignore_testfiles")
        os.makedirs("data", exist_ok=True)
        os.chdir("data")
        os.makedirs("sample", exist_ok=True)
        os.chdir("sample")
        with open('.gitignore', 'w') as f:
            f.write("""
# Start of gitignore
*.html
# End of gitignore""")
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.chdir("file_globs_gitignore_testfiles")
        files = [
            os.path.join("src", "main.c"),
            os.path.join("src", "main.h"),
            os.path.join("src", "lib", "ssl.c"),
            os.path.join("src", "tests", "main.c"),
            os.path.join("src", "main.py"),
            os.path.join("src", "upload.c"),
            os.path.join("another_folder", "another_file.c"),
            os.path.join("data", "sample", "index.css"),
            os.path.join("data", "example.py"),
            ".coafile"
        ]
        ignored_files = [
            os.path.join("build", "main.c"),
            os.path.join("tests", "run.c"),
            os.path.join("src", "build", "main.c"),
            "ignore.c",
            os.path.join("src", "ignore.c"),
            "globexp.py",
            "upload.c",
            os.path.join("src", "main.pyc"),
            os.path.join("another_folder", "script.js"),
            os.path.join("data", "sample", "index.html"),
            "run.pyc"
        ]

        for file in files + ignored_files:
            os.makedirs(os.path.dirname(os.path.abspath(file)), exist_ok=True)
            open(file, "w").close()
        files += [".gitignore"]
        files += [os.path.join("another_folder", ".gitignore")]
        files += [os.path.join("data", "sample", ".gitignore")]

        gitignore_dir_list = [os.getcwd(),
                              os.path.join(os.getcwd(), "another_folder"),
                              os.path.join(os.getcwd(), "data", "sample")]
        globs = list(get_gitignore_glob(os.getcwd(), gitignore_dir_list))
        returned_files = collect_files(
            [os.path.join(os.getcwd(), "**")],
            self.log_printer,
            ignored_file_paths=globs)
        files = [os.path.normcase(os.path.abspath(file)) for file in files]
        ignored_files = [os.path.abspath(file) for file in ignored_files]
        self.maxDiff = None
        self.assertEqual(sorted(files), sorted(returned_files))

        with suppress_stdout():
            self.assertEqual(
                sorted(get_project_files(
                    self.log_printer, self.printer, os.getcwd())[0]),
                sorted(files))

        os.remove(os.path.join("another_folder", ".gitignore"))
        os.remove(os.path.join("data", "sample", ".gitignore"))
        os.remove(".gitignore")
        os.chdir(orig_cwd)

    def test_get_project_files_ci_mode(self):
        orig_cwd = os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)) +
                 os.sep + "file_globs_ci_testfiles")

        with suppress_stdout():
            res, _ = get_project_files(
                self.log_printer, self.printer, os.getcwd(), True)

            paths = [
                os.path.join(os.getcwd(), "src", "file.c"),
                os.path.join(os.getcwd(), "root.c"),
                os.path.join(os.getcwd(), "ignore_dir", "src.c"),
                os.path.join(os.getcwd(), "ignore_dir", "src.js"),
            ]

            for path in paths:
                self.assertIn(os.path.normcase(path), res)

        os.chdir(orig_cwd)
