# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os, sys

version = '0.1.0'
long_description = '\n'.join([
        #open(os.path.join("src","README.txt")).read(),
        #open(os.path.join("src","AUTHORS.txt")).read(),
        #open(os.path.join("src","HISTORY.txt")).read(),
        ])

classifiers = [
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Topic :: Software Development",
]

setup(
    name = 'gaefw',
    version = version,
    description='',
    long_description=long_description,
    classifiers=classifiers,
    keywords=['GAE', 'nose', 'test'],
    author='Takayuki SHIMIZUKAWA',
    author_email='shimizukawa at gmail dot com',
    url='http://bitbucket.org/shimizukawa/gaefw',
    license='MIT',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data = {'': ['buildout.cfg']},
    include_package_data=True,
    install_requires=[
        'setuptools',
        'jinja2',
    ],
    extras_require = {
        'test': [
            'nose',
        ],
    },
    entry_points = {
        'nose.plugins.0.10': [
            'gaefw.test.gaeplugin = gaefw.test.gaeplugin:Test',
        ],
    },
    zip_safe=False,
)

