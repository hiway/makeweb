#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import (
    absolute_import,
    print_function
)

import io
from os.path import (
    dirname,
    join,
)

from setuptools import find_packages, setup


def read(*names, **kwargs):
    return io.open(
            join(dirname(__file__), *names),
            encoding=kwargs.get('encoding', 'utf8')
    ).read()


setup(
        name='makeweb',
        version='0.1.0',
        license='MIT',
        description='',
        long_description=read('README.md'),
        author='Harshad Sharma',
        author_email='harshad@sharma.io',
        url='https://github.com/hiway/makeweb',
        py_modules=['makeweb'],
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT',
            'Operating System :: Unix',
            'Operating System :: POSIX',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: Implementation :: CPython',
            'Topic :: Internet',
            'Topic :: Software Development',
            'Topic :: Utilities',
        ],
        keywords=[
            'website',
            'html',
            'css',
            'javascript',
            'generate',
            'template',
        ],
        install_requires=[
        ],
        extras_require={
            'dev': [
                'pytidylib',
                'jsmin',
                'javascripthon',
                'flask',
                'pytest',
                'pytest-cov',
            ],
            'js': [
                'jsmin',
                'javascripthon',
            ],
            'examples': [
                'faker',
                'markdown',
                'flask',
                'tinydb',
                'jsmin',
                'javascripthon',
            ],
        },
)
