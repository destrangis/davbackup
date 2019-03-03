#! /usr/bin/env python3

from setuptools import setup

with open("README.md") as readme:
    long_descr = readme.read()

setup(
    name="davbackup",
    version="0.1.0",
    py_modules=["davbackup"],
    author="Javier Llopis",
    author_email="javier@llopis.me",
    url="http://mikrodev:3000/javier/davbackup",
    description="Make backups of a DAV Server.",
    long_description=long_descr,
    entry_points = {
        'console_scripts': ['davbackup=davbackup:main'],
    },
    install_requires = [
        "easywebdav2>=1.3.0",
        "requests>=2.18.4",
    ],
    classifiers='''Programming Language :: Python
    Programming Language :: Python :: 3 :: Only
    License :: OSI Approved :: MIT License
    Development Status :: 4 - Beta
    Environment :: Console
    Intended Audience :: End Users/Desktop
    Intended Audience :: System Administrators
    Operating System :: OS Independent
    Topic :: Internet :: WWW/HTTP
    Topic :: System :: Archiving :: Backup
    Topic :: System :: Archiving :: Mirroring
    Topic :: Utilities
    '''
)
