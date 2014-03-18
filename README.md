RIPE Atlas Command Line Manager
========================
[![Build Status](https://travis-ci.org/astrikos/ripe-atlas-cmdline.png?branch=master)](https://travis-ci.org/astrikos/ripe-atlas-cmdline) [![Code Health](https://landscape.io/github/astrikos/ripe-atlas-cmdline/master/landscape.png)](https://landscape.io/github/astrikos/ripe-atlas-cmdline/master)
Overview
--------------------
A modular and extendable manager for RIPE Atlas API.
Gives you basic commands to use the API with a friendlier way from command line.
Example of available commands are the creation of a UDM, showing of meta data
and results download.
Using the manager
---------------------
In order to use the manager you have to run:

        ./atlas_manage.py <command> [options].

Running just:

        ./atlas_manage.py

will list you the already existent commands.

If you want to see the additional options for every command use -h option e.g.

        ./atlas_manage.py create -h

Specifing:

        ./atlas_manage.py create --help_text

as an option will show you a small description for every command.
Adding Commands
----------------------
A new command can be added by adding a python file inside commands directory and
create a class with the name Command. There is a template example that anyone 
can use and write its own commands following the template.
