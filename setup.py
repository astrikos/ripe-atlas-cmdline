#!/usr/bin/env python

from setuptools import setup, find_packages

__version__ = "0.2"
install_requires = []
tests_require = [
    'nose',
    'coverage',
    'mock',
    'jsonschema'
]

setup(
    name='atlascli',
    version=__version__,
    description='Python command line tool for RIPE ATLAS API',
    author="Andreas Strikos",
    author_email="andreas@strikos.name",
    packages=find_packages(
        where='.',
        exclude=('tests*', )
    ),
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite="nose.collector",
    scripts=["scripts/atlas-manage"]
)
