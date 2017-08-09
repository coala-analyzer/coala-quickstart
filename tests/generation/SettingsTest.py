import os
import sys
import tempfile
import unittest
from datetime import date
from copy import deepcopy

from pyprint.ConsolePrinter import ConsolePrinter

from coalib.output.ConfWriter import ConfWriter
from coala_quickstart.coala_quickstart import _get_arg_parser
from coala_quickstart.generation.Settings import write_info, generate_settings
from coala_quickstart.generation.Bears import filter_relevant_bears
from coala_quickstart.generation.Project import get_used_languages


class SettingsTest(unittest.TestCase):

    def setUp(self):
        self.project_dir = os.getcwd()
        self.printer = ConsolePrinter()
        self.coafile = os.path.join(tempfile.gettempdir(), '.coafile')
        self.writer = ConfWriter(self.coafile)
        self.arg_parser = _get_arg_parser()
        self.old_argv = deepcopy(sys.argv)
        del sys.argv[1:]

    def tearDown(self):
        self.writer.close()
        os.remove(self.coafile)
        sys.argv = self.old_argv

    def test_write_info(self):
        result_date = date.today().strftime('%d %b %Y')
        result_comment = ('# Generated by coala-quickstart on '
                          '{date}.\n'.format(date=result_date))
        write_info(self.writer)
        self.writer.close()

        with open(self.coafile, 'r') as f:
            line = f.readline()

        self.assertEqual(result_comment, line)

    def test_allow_complete_section_mode(self):
        project_dir = '/repo'
        project_files = ['/repo/hello.html']
        ignore_globs = []

        used_languages = list(get_used_languages(project_files))
        relevant_bears = filter_relevant_bears(
            used_languages, self.printer, self.arg_parser, {})

        res = generate_settings(
            project_dir, project_files, ignore_globs, relevant_bears, {}, True)

        bears_list = res['all.HTML']['bears'].value.replace(' ', '').split(',')

        files_list = res['all.HTML']['files'].value.replace(' ', '').split(',')

        self.assertEqual(
            ['HTMLLintBear', 'coalaBear', 'BootLintBear',
             'LicenseCheckBear', 'SpaceConsistencyBear', 'KeywordBear',
             'LineLengthBear', 'DuplicateFileBear'].sort(),
            bears_list.sort())

        self.assertEqual(['**.html'], files_list)
