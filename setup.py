#! /usr/bin/env python3

from setuptools import setup
import re

with open("davbackup.py") as fd:
    source = fd.read()
VERSION = re.search(r'^VERSION\s*=\s*\"([^"]+)', source, re.MULTILINE).group(1)
    

with open("README.rst") as readme:
    long_descr = readme.read()

setup(
    name="davbackup",
    version=VERSION,
    py_modules=["davbackup"],
    author="Javier Llopis",
    author_email="javier@llopis.me",
    url="https://github.com/destrangis/davbackup",
    description="Make backups of a DAV Server.",
    license="MIT",
    long_description_content_type="text/x-rst",
    long_description=long_descr,
    entry_points={"console_scripts": ["davbackup=davbackup:main"]},
    install_requires=["easywebdav2>=1.3.0", "requests>=2.18.4"],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: System :: Archiving :: Mirroring",
        "Topic :: Utilities",
    ],
)
