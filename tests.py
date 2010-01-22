# encoding: utf-8
"""
loopozorg's test suite

run with nose http://somethingaboutorange.com/mrl/projects/nose
"""

from itertools import imap
from os.path import isfile, join
from shutil import rmtree
from tempfile import mkdtemp
from time import sleep

from nose.tools import assert_equals, raises

from loopozorg import Loop, create_file_if_it_doesnt_exist, \
                      _get_caller_filename, get_mtime, open_file_in_editor


__author__ = 'Maciej Konieczny <hello@narf.pl>'


class TestAttributes:

    def test_set_default_values_on_clean_init(self):
        loop = Loop(parameters=[])
        for actual, expected in [
            (loop.raw, ''),
            (loop.passed_special, False),
            (loop.tracked_files, []),
            (loop.main_file, ''),
            (loop.bin, ''),
            (loop.args, ''),
        ]:
            assert_equals(actual, expected)

    def test_parse_input(self):
        # parameters
        parameters = ['+']
        passed_special = True

        tracked_files = ['foo', 'bar']
        parameters.extend(tracked_files)

        main_file = tracked_files[0]

        bin = main_file

        args = '-3 --verbose reset --hard'
        parameters.extend(args.split())

        # test
        loop = Loop(parameters=parameters)
        for actual, expected in [
            (loop.raw, ' '.join(parameters)),
            (loop.passed_special, passed_special),
            (loop.tracked_files, tracked_files),
            (loop.main_file, main_file),
            (loop.bin, bin),
            (loop.args, args),
        ]:
            assert_equals(actual, expected)

    def test_represent_attributes_as_dict_of_strs(self):
        passed_special = 'False'
        main_file = 'baz'
        bin = main_file
        tracked_files = main_file + ' foo bar'
        args = '--waka -waka waka'
        raw = tracked_files + ' ' + args

        expected = {
            'raw': raw,
            'passed_special': passed_special,
            'tracked_files': tracked_files,
            'main_file': main_file,
            'bin': bin,
            'args': args,
        }

        loop = Loop(parameters=raw.split())
        actual = loop._get_attrs_as_dict_of_strs()

        assert_equals(actual, expected)

    def test_escape_raw(self):
        expected = "'foo bar' baz"
        actual = Loop(parameters=['foo bar', 'baz']).raw
        assert_equals(actual, expected)

    def test_escape_paths(self):
        tracked_files = ['some file', 'main file']
        loop = Loop(parameters=tracked_files)
        attrs = loop._get_attrs_as_dict_of_strs()
        for key, expected in [
            ('tracked_files', ' '.join(imap(repr, tracked_files))),
            ('main_file', repr(tracked_files[0])),
            ('bin', repr(tracked_files[0])),
        ]:
            actual = attrs[key]
            assert_equals(actual, expected)

    def test_use_userdefined_attributes(self):
        loop = Loop(parameters=[])
        loop.foo = None
        expected = 'None'
        actual = loop._get_attrs_as_dict_of_strs()['foo']
        assert_equals(actual, expected)

    def test_strip_main_file_extension_in_bin(self):
        expected = 'foo'
        actual = Loop(parameters=[expected + '.bar']).bin
        assert_equals(actual, expected)


class TestCreateFile:

    def setup(self):
        """
        Create temporary directory.
        """

        self.directory = mkdtemp()

    def teardown(self):
        """
        Remove temporary directory.
        """

        rmtree(self.directory)


    def test_dont_create_file_if_it_already_exists(self):
        # create test file
        filepath = join(self.directory, 'foo')
        with open(filepath, 'w'):
            pass
        mtime_before = get_mtime(filepath)
        sleep(1)  # one second

        create_file_if_it_doesnt_exist(filepath)
        mtime_after = get_mtime(filepath)

        assert_equals(mtime_before, mtime_after)

    def test_create_file_if_it_doesnt_exist(self):
        filepath = join(self.directory, 'foo')
        create_file_if_it_doesnt_exist(filepath)
        assert isfile(filepath), 'File not created'

    def test_use_template(self):
        template = join(self.directory, 'template')
        content = 'waka waka waka'
        with open(template, 'w') as f:
            f.write(content)

        filepath = join(self.directory, 'foo')
        create_file_if_it_doesnt_exist(filepath, template)

        with open(filepath) as f:
            assert_equals(f.read(), content)

    def test_get_caller_name(self):
        assert_equals(_get_caller_filename(), 'nosetests')


class TestOpenFile:

    @raises(EnvironmentError)
    def test_raise_exception_if_EDIT_is_not_set(self):
        open_file_in_editor(filepath=None, edit='')
