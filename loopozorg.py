#!/usr/bin/env python
# encoding: utf-8
"""
Execute shell command on file modification.
"""

from inspect import stack
from itertools import imap
from os import environ, stat
from os.path import basename, dirname, expanduser, isfile, join, realpath, \
                    splitext
from pipes import quote
from shutil import copy
from subprocess import call
import sys
from time import sleep


__author__ = 'Maciej Konieczny <hello@narf.pl>'


class Loop(object):

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

        attrs['tracked_files'] = ' '.join(imap(quote, self.tracked_files))
        attrs['main_file'] = quote(self.main_file)
        attrs['bin'] = quote(self.bin)

        for k, v in attrs.iteritems():
            if not isinstance(v, str):
                attrs[k] = str(v)

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

        while True:
            new_mtime_sum = sum(imap(get_mtime, self.tracked_files))
            if old_mtime_sum != new_mtime_sum:
                old_mtime_sum = new_mtime_sum
                call('clear;' + command, shell=True)
            sleep(1)  # one second


def create_file_if_it_doesnt_exist(filepath, template=None):
    if not isfile(filepath) and template is not None:
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

    Use environment variable $EDIT.  It should be set according to $EDITOR and
    should open editor in background -- $EDITOR usually opens editor in
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
