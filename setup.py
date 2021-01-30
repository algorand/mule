#!/usr/bin/env python
import setuptools as setuptools

from mule import __version__

setuptools.setup(
    name='mulecli',
    version=__version__,
    description='Script for executing automated tasks',
    packages=setuptools.find_packages(),
    python_requires='>=3.5',
    include_package_data=True,
    install_requires=[
        'boto3',
        'botocore',
        'gitpython',
        'packaging',
        'pygithub',
        'pystache',
        'pytest',
        'pyyaml',
        'wget',
    ],
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
    entry_points={
        "console_scripts": [
            "mule = mule.main:main",
            "muleci = mule.poc.driver:main"
        ],
        "mule.plugin": [
            "docker = mule.task.docker",
            "s3 = mule.task.s3",
            "shell = mule.task.shell",
            "stash = mule.task.stash",
        ],
    }
)
