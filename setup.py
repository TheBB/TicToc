#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='TicToc',
    version='0.1.0',
    description='Astronometry experiments',
    maintainer='Eivind Fonn',
    maintainer_email='evfonn@gmail.com',
    url='https://github.com/TheBB/TicToc',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['tictoc=tictoc.__main__:main'],
    },
    install_requires=[
        'click',
    ],
)
