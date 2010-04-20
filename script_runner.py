#!/usr/bin/env python
# encoding: utf-8
"""
loopozorg script runner

Canonically this utility is located in `~/.loops/loopozorg/`.  It should
be given a short alias, e.g. "loop"

    alias loop="python ~/.loops/loopozorg/script_runner.py"

This way if you want to run a loopozorg script called `pacman.py`
(located in `~/.loops/`) with "waka-waka-waka" parameter, all you have
to do is

    loop pacman waka-waka-waka

"""

from itertools import imap
from os.path import dirname, isfile, join, realpath
from pipes import quote
from subprocess import call
from sys import argv, stderr


__author__ = 'Maciej Konieczny <hello@narf.pl>'


def _main():
    if len(argv) < 2:
        print >> stderr, __doc__[1:-1]
        exit(1)

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
