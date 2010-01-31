loopozorg
=========

Infrastructure for executing shell commands on file modification.

When writing code, you often have to take an additional action to see
the result of what you've just written.  This is true regardless you
write Python, C, HTML or LaTeX -- after saving the source code file, you
have to run the compiler, interpreter, validator, test suite or simply
refresh your browser.  These tasks are extremely boring, repetitive,
distracting and force you to do too many things--like changing the
active window to a terminal, reentering the last command and going back
to your editor--just to discover you didn't put a semicolon at the end
of that stupid line.

loopozorg is the ⌘S instead of ⌘S ⌘⇥ ↑ ↩ ⌘⇥.  It provides you a way of
writing super-short Python scripts containing reusable commands that are
executed every time any tracked file is modified.  Even if you don't
know Python, you should be able to write your own loop scripts just by
looking at the examples.


Features
--------

  - Python
  - real-life, fully operational, reusable loop scripts in two lines of
    code
  - ability to automatically open file in editor before running a loop
  - file creation with basic template support
  - automatic template assignment
  - loop script runner


Overview
--------

The idea behind loopozorg is simple: a set of shell commands you run to
process your files is saved in a file.  This file is called "loop".
Every loop is a Python script located in `~/.loops/`.  Every loop script
imports and instantiates `Loop` object, which does most of the magic --
it parses command line parameters and executes your commands every time
any tracked file is modified.

Accepted command line parameters format is

    [+] [file1 file2 ...] [-arg1 arg2 ...]

This means all parameters are optional.  First parameter is called
"special" and it is a plus sign.  It is followed by file paths separated
by spaces.  Arguments are the last element, first of them has to start
with a dash.

Parameters are represented by `Loop` attributes:

  - `raw` -- string representing all parameters
  - `passed_special` -- boolean indicating whether first parameter is a
    plus sign
  - `tracked_files` -- list of file paths
  - `args` -- string representing arguments

`Loop` also provides two properties (attributes that you can't change):

  - `main_file` -- first tracked file
  - `bin` -- main file without extension


The exciting thing is that `Loop` attributes and properties can be used
in your commands as [replacement fields][rf] (see the Example section),
which makes it possible to write loop scripts in two lines of code.

  [rf]: http://docs.python.org/library/string.html#format-string-syntax

There are two ways of using `Loop`:

  1. You can instantiate it with a single string argument, which is the
     command that will be executed.  In this case there is no need to
     assign returned object to any variable, because command is passed
     to the `run` method, which starts an infinite loop.

  2. You can instantiate it without any arguments, change attributes of
     returned object (and/or add new) and manually call the `run` method
     with desired set of arguments (see its docstring for more
     information).


If special parameter is passed, loopozorg will try to create main file
(if it doesn't exist) using a template located in `~/.loops/templates/`
and named after loop script (see the Example section).  If template is
not found, empty file will be created.  loopozorg will also try to open
main file in editor.  It uses environment variable `$EDIT` to do this.
You should set it according to `$EDITOR`.  It should open editor in
background -- `$EDITOR` usually opens it in foreground, which holds the
loop.  Calling `run` method with `enable_special=False` argument
disables features described in this paragraph.

loopozorg provides a convenient loop script runner, see Example and
Installation sections for usage and installation information.


Example
-------

Suppose you write a lot of Python.  There's a loop for that:

    cat - > ~/.loops/python.py
    from loopozorg import Loop
    Loop('python {main_file} {args}; pyflakes {tracked_files}')
    ^D

While writing such code is not the best practice (loop would start, had
someone imported this file), it's perfectly valid and does the job in
two lines of code.  Now you can run your `foo.py` script with

    loop python foo.py

It will be executed every time you save it.  Also, [PyFlakes][] will
tell you, if your code has any defects.

  [PyFlakes]: http://divmod.org/trac/wiki/DivmodPyflakes

What if you don't have any `foo.py` file?  Well, you can run

    loop python + foo.py

and before starting a loop, loopozorg will create `foo.py` and open it
in editor.  It won't overwrite your file if it already exists.  But if
it doesn't, loopozorg will try to create it using a template named after
loop script -- in this case it would use
`~/.loops/templates/python.txt`.

If you're willing to add another file to your project, run

    loop python foo.py bar.py

Every time you save any of these two files, `foo.py` will be executed
and both files will be checked by PyFlakes.

If you'd like to pass some arguments to your script, you can!  They have
to be placed after file paths and the first argument has to start with a
dash -- otherwise it will be interpreted as another file.  That said, a
possible way of running a loop is

    loop python foo.py -n 37


Of course all these features can be used together, so you can run your
loop like this

    loop python + pacman.py ghosts.py --waka-waka


Visit [~narfdotpl/.loops][narf loops] for more examples.

  [narf loops]: http://github.com/narfdotpl/dotfiles/tree/master/.loops


Installation
------------

Following installation notes are guidelines, not instructions -- stop,
if you don't know what you're doing. [Python][] (2.6 <=  version < 3.0)
is required.

  [Python]: http://python.org/


Get loopozorg

    mkdir ~/.loops
    cd ~/.loops
    git clone git://github.com/narfdotpl/loopozorg


Alias script runner, e.g.

    cat - >> ~/.profile
    alias loop="python ~/.loops/loopozorg/script_runner.py"
    ^D


Set `$EDIT`, e.g.

    cat - >> ~/.profile
    export EDIT="mvim"
    ^D


Meta
----

loopozorg is written by [Maciej Konieczny][].  This software is released
into the [public domain][].

  [Maciej Konieczny]: http://narf.pl/
  [public domain]: http://unlicense.org/
