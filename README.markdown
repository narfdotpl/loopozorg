loopozorg
=========

Infrastructure for executing shell commands on file modification.

When writing code, you often have to take an additional action to
see results of what you've just written.  This is true regardless
you write Python, Ruby, C, JavaScript, Markdown or LaTeX -- after
making a change in source code, you have to run compiler, interpreter,
validator, test suite... or simply refresh browser.  These activities
are distracting and force you to do too many things--like switching to
terminal, reentering previous command and going back to editor--just to
discover you didn't put a semicolon at the end of that stupid line.

loopozorg is ⌘S instead of ⌘S ⌘⇥ ↑ ↩ ⌘⇥.  It lets you write short,
reusable Python scripts that track your files and execute shell commands
when these files are modified.  Even if you don't know Python, you will
be able to write your own loop scripts just by looking at examples.


Example
-------

(code speaks louder than words)

    $ cat ~/.loops/python.py
    from loopozorg import Loop
    Loop('python {main_file} {args}; pyflakes {tracked_files}')

    $ loop python pacman.py ghosts.py --waka-waka


Visit [~narfdotpl/.loops][narf loops] for more examples.

  [narf loops]: http://github.com/narfdotpl/dotfiles/tree/master/home/.loops


Features
--------

  - Python
  - reusable, real-life loop scripts in two lines of code
  - file creation with basic template support
  - ability to automatically open file in editor before running a loop


Overview
--------

The idea behind loopozorg is simple: you save sequence of shell commands
in a file and put it in `~/.loops/` directory.  This file is a Python
script.  It imports and instantiates a `Loop` object.  By default,
`Loop` parses command line parameters that script is called with.  It
expects them to be in the following format:

    [+] [file1 file2 ...] [-arg1 arg2 ...]

All parameters are optional.  The first one is a plus and it's called
"special".  It is followed by file paths.  Arguments are at the end,
first of them has to start with a minus.

You can access parsed parameters via `Loop` attributes:

  - `raw` -- string representing all parameters
  - `passed_special` -- boolean indicating whether first parameter is
    a plus
  - `tracked_files` -- list of file paths
  - `args` -- string representing arguments

`Loop` also provides two properties (attributes that you can't change):

  - `main_file` -- first tracked file
  - `bin` -- main file without extension


`Loop` properties and attributes--both built-in and created by you--can
be used as [replacement fields][rf] in your commands (see *Step by step
example* section).

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


Apart from parsing parameters, another thing that loopozorg does by
defualt is creating main file using template and opening it in editor.
loopozorg does this if loop script is run with special parameter
("+"); you can disable this feature by calling `run` method with
`enable_special=False` argument.  File creation and template support is
described in *Step by step example* section; here I'll focus on opening
files in editor. loopozorg uses environment variable `$EDIT` to do this.
You should set it according to `$EDITOR`.  It should open editor in
background -- `$EDITOR` usually opens it in foreground, which holds the
loop.

loopozorg provides a convenient loop script runner, called `loop`.
See *Step by step example* and *Installation* sections for usage and
installation information.


Step by step example
--------------------

### Your first loop script

Suppose you write a lot of Python.  There's a loop for that:

    $ cat - > ~/.loops/python.py
    from loopozorg import Loop
    Loop('python {main_file} {args}; pyflakes {tracked_files}')
    ^D

While writing such code is not a best Python practice (loop would start,
had someone imported this file), it's perfectly valid and does the job
in two lines of code.  Now you can run a `pacman.py` script with

    $ loop python pacman.py

It will be executed every time you save it.  Also, [PyFlakes][] will
tell you if your code has any defects.  (You can also run this loop
like you would run any Python script -- with `python ~/.loops/python.py
pacman.py` command).

  [PyFlakes]: http://divmod.org/trac/wiki/DivmodPyflakes


### File creation and template support

What if there's no `pacman.py` file?  Well, if you run

    $ loop python + pacman.py

loopozorg will check, whether `pacman.py` exists.  If it does, loopozorg
will open it in editor.  If it doesn't exist, loopozorg will try to
create it using a template named after loop script you're using (in this
case it would try to use `~/.loops/templates/python.txt`).  If there's
no template, an empty file will be created.  After creating a file,
loopozorg will open it in editor.


### Many tracked files

If you want to add another file to your project, run

    $ loop python pacman.py ghosts.py

Every time you save any of these two files, `pacman.py` will be executed
and both files will be checked by PyFlakes.


### Arguments

You can pass arguments to your scripts.  They have to be placed after
file paths and first argument has to start with a minus -- otherwise it
will be interpreted as another file path.  So if you want to execute
`pacman.py` script with a `--waka-waka` argument, run

    $ loop python pacman.py --waka-waka


### Rule them all

Of course, all loopozorg features can be used together:

    $ loop python + pacman.py ghosts.py --waka-waka


Installation
------------

Following installation notes are guidelines, not instructions -- stop,
if you don't know what you're doing. [Python][] (2.6 <= version < 3.0)
is required.

  [Python]: http://python.org/


 1. get loopozorg

        $ mkdir ~/.loops
        $ cd !$
        $ git clone http://github.com/narfdotpl/loopozorg.git

 2. put `loop` in your `$PATH` (optional)

        $ ln -s ~/.loops/loopozorg/loop ~/bin

 3. set `$EDIT` (optional)

        $ cat - >> ~/.profile
        export EDIT="mvim"
        ^D


Meta
----

loopozorg is written by [Maciej Konieczny][].  This software is released
into the [public domain][] and uses [semantic versioning][] for release
numbering.

  [Maciej Konieczny]: http://narf.pl/
  [public domain]: http://unlicense.org/
  [semantic versioning]: http://semver.org/
