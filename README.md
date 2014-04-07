RIPE Atlas Command Line Manager
==============================
[![Build Status](https://travis-ci.org/astrikos/ripe-atlas-cmdline.png?branch=master)](https://travis-ci.org/astrikos/ripe-atlas-cmdline) [![Code Health](https://landscape.io/github/astrikos/ripe-atlas-cmdline/master/landscape.png)](https://landscape.io/github/astrikos/ripe-atlas-cmdline/master) [![Coverage Status](https://coveralls.io/repos/astrikos/ripe-atlas-cmdline/badge.png?branch=master)](https://coveralls.io/r/astrikos/ripe-atlas-cmdline?branch=master)
Overview
--------
A modular and extendable manager for RIPE Atlas API.
Gives you basic commands to use the API with a friendlier way from command line.
Example of available commands are the creation of a UDM, showing of meta data
and results download.

Installation
------------
You can install by either cloning the repo and run the following inside the repo:

        $ python setup.py install

or via pip using:

        $ pip install https://github.com/astrikos/ripe-atlas-cmdline/zipball/master

Using the manager
-----------------
In order to use the manager you have to run:

        $ ./atlas-manage <command> [options].

Running just:

        $ ./atlas-manage

will list you the already existent commands.

If you want to see the additional options for every command use -h option e.g.

        ./atlas-manage create -h

Specifing:

        $ ./atlas-manage create --help_text

as an option will show you a small description for every command.
Adding Commands
---------------
A new command can be added by adding a python file inside commands directory and
create a class with the name Command. There is a template example that anyone 
can use and write its own commands following the template.
