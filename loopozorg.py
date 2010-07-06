#!/usr/bin/env python
# encoding: utf-8
"""
Infrastructure for executing shell commands on file modification.

The heart of this module is the `Loop` class -- see its docstrings for
more information (I assume you're familiar with the README).
"""

from collections import Sequence
from inspect import stack
from itertools import imap
from os import environ, stat
from os.path import basename, dirname, exists, expanduser, isfile, join, \
                    realpath, splitext
from pipes import quote
from shutil import copy
from subprocess import call
import sys
from time import sleep


__author__ = 'Maciej Konieczny <hello@narf.pl>'
__version__ = '0.3.0dev'


class Loop(object):
    """
    loopozorg's <3
    ==============

    The constructor parses command line parameters* and sets the following
    attributes:

      - `raw` -- string representing all parameters
      - `passed_special` -- boolean indicating whether first parameter is
        a plus
      - `args` -- substring of `raw`, it begins with first parameter that
        starts with a minus
      - `tracked_files` -- list of file paths; that is all parameters apart
        from `args` and special parameter

    The constructor also sets two properties:

      - `main_file` -- first tracked file
      - `bin` -- main file without extension


    There are two ways of using this class:

      1. Instantiating it with a single string argument, which is the
         command that will be executed, i.e.

             Loop('python {main_file} {args}; pyflakes {tracked_files}')

         In this case there is no need to assign returned object to any
         variable, because command is passed to the `run` method, which
         starts an infinite loop.  This way you can write real-life, fully
         operational loop scripts in two lines of code: import line and
         `Loop('...`.

      2. Instantiating it without any arguments, changing attributes of
         returned object (and/or adding new) and manually calling the `run`
         method with desired set of arguments (see its docstring for more
         information).

    ----------------
    * I use the word "parameters" instead of "arguments" to prevent
      confusion with the `args` attribute.
    """

    def __init__(self, command=None, parameters=sys.argv[1:]):
        # set default values
        self.raw = ' '
        self.passed_special = False
        self.tracked_files = []
        self.args = ''

        # get raw
        self.raw = ' '.join(imap(quote, parameters))

        # get special
        if parameters and parameters[0] == '+':
            self.passed_special = True
            parameters = parameters[1:]

        if parameters:
            # get args
            for i, parameter in enumerate(parameters):
                if parameter.startswith('-'):
                    self.args = ' '.join(parameters[i:])
                    break
            else:  # if no break
                i += 1

            # get tracked files
            self.tracked_files = parameters[:i]

        if command:
            self.run(command)

    def _get_attrs_as_dict_of_strs(self):
        attrs = self.__dict__.copy()

        # add properties
        attrs['tracked_files'] = self.tracked_files
        attrs['main_file'] = quote(self.main_file)
        attrs['bin'] = quote(self.bin)

        # convert everything to strings
        for key, value in attrs.iteritems():
            if not isinstance(value, basestring):
                if isinstance(value, Sequence):
                    # convert sequence to string of space-separated,
                    # quoted elements
                    attrs[key] = ' '.join(imap(quote, imap(str, value)))
                else:
                    attrs[key] = str(value)

        return attrs

    @property
    def bin(self):
        return splitext(self.main_file)[0]

    @property
    def main_file(self):
        if self.tracked_files and isinstance(self.tracked_files, list):
            return self.tracked_files[0]
        else:
            return ''

    def run(self, command, template=None, enable_autotemplate=True,
            enable_special=True):
        """
        Every second check if any tracked file has been modified.  If it has,
        clear the screen and execute the `command`.

        Subject `command` to string formatting -- replace fields with string
        representations of corresponding attributes, e.g. if `main_file` is
        "README.txt" and `command` is "cat {main_file}", change it to "cat
        README.txt".

        If `enable_special` is true and special parameter was passed, create
        main file (if it doesn't exist) and open it in editor.

        If `template` file path is not given and `enable_autotemplate` is true,
        use script's name to generate template path, e.g. when script name is
        `python.py`, set `template` to `~/.loops/templates/python.txt`
        (assuming loopozorg's location is `~/.loops/loopozorg`).
        """

        if enable_special and self.passed_special:
            if enable_autotemplate and template is None:
                templates_dir = realpath(join(
                    dirname(__file__), '../templates'
                ))
                caller_filename = _get_caller_filename()
                template_filename = splitext(caller_filename)[0] + '.txt'
                template = join(templates_dir, template_filename)

            create_file_if_it_doesnt_exist(self.main_file, template)
            open_file_in_editor(self.main_file)

        command = command.format(**self._get_attrs_as_dict_of_strs())
        old_mtime_sum = -1

        with exit_on_ctrl_c():
            while True:
                new_mtime_sum = sum(imap(get_mtime, self.tracked_files))
                if old_mtime_sum != new_mtime_sum:
                    old_mtime_sum = new_mtime_sum
                    call('clear;' + command, shell=True)
                sleep(1)  # one second


class exit_on_ctrl_c(object):

    def __init__(self, quiet=False):
        self.quiet = quiet

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is KeyboardInterrupt:
            if not self.quiet:
                print '\nexiting'
            exit()


def create_file_if_it_doesnt_exist(filepath, template=None):
    if not exists(filepath):
        if template is not None:
            template = expanduser(template)
            if isfile(template):
                copy(template, filepath)
        else:
            with open(filepath, 'a'):
                pass


def _get_caller_filename():
    return basename(stack()[-1][1])


def get_mtime(filepath):
    try:
        return stat(filepath).st_mtime
    except OSError:  # except file doesn't exist
        return 0


def open_file_in_editor(filepath, edit=None):
    """
    Open file in editor.

    Use environment variable $EDIT.  It should be set according to $EDITOR
    and should open editor in background -- $EDITOR usually opens editor in
    foreground, which holds the loop.
    """

    if edit is None:
        edit = environ.get('EDIT', None)

    if edit:
        call(edit + ' ' + filepath, shell=True)
    else:
        docstring_line_number = stack()[0][2] - 11
        raise EnvironmentError(
            'Environment variable $EDIT not set; see {0}, line {1}' \
            .format(__file__, docstring_line_number)
        )
