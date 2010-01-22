#!/usr/bin/env python
# encoding: utf-8
"""
loopozorg script runner
"""

from itertools import imap
from os.path import dirname, isfile, join, realpath
from pipes import quote
from subprocess import call
from sys import argv


__author__ = 'Maciej Konieczny <hello@narf.pl>'


def usage():
    print(__doc__)


def _main():
    if len(argv) < 2:
        usage()
    else:
        loop_name = argv[1] + '.py'
        parameters = ' '.join(imap(quote, argv[2:]))

        loops_dir = join(dirname(__file__), '..')
        loop_path = realpath(join(loops_dir, loop_name))

        if isfile(loop_path):
            call('python {0} {1}'.format(loop_path, parameters), shell=True)
        else:
            print('File not found: ' + loop_path)

if __name__ == '__main__':
    _main()