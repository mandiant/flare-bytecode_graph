#!/usr/bin/env python

from setuptools import setup

setup(name='bytecode_graph',
      version="1.0",
      description="Module to manipulate and analyze Python bytecode",
      author='Joshua Homan',
      author_email='joshua.homan@fireeye.com',
      url='https://github.com/fireeye/flare-bytecode_graph',
      license='Apache License (2.0)',
      packages=['bytecode_graph'],
      classifiers=["Programming Language :: Python",
                   "Programming Language :: Python :: 2",
                   "Operating System :: OS Independent",
                   "License :: OSI Approved :: Apache Software License"],
      install_requires=["pydot"])
