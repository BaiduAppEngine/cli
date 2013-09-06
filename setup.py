#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
Bae Client contains main apis for BAE

@Author    : zhangguanxing01@baidu.com
@Copyright : 2013 Baidu Inc. 
@Date      : 2013-06-26 11:09:00
'''



import os
import sys
from   bae.config.constants import VERSION

try:
    from setuptools import *
except ImportError:
    from distutils.core import *

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

if os.environ.has_key("BAE_OFFLINE"):
    offline = os.environ["BAE_OFFLINE"]
else:
    offline = "yes"

if sys.argv[-1] == "publish":
    os.system("rm -rf bae.egg-info")
    os.system("rm -rf build")
    os.system("rm -rf dist")
    os.system("find . -name '*.pyc' | xargs rm -rf")
    sys.exit(-1)

requires = ['requests', 'colorama', 'pycrypto', 'PyYAML', 'prettytable>=0.7.0']

setup(
    name = "bae",
    version = VERSION,
    author = "Zhang Guanxing",
    author_email = "zhangguanxing01@baidu.com",
    description = ("A BAE Client Tool"),
    keywords = "bae client tool",
    url = "http://developer.baidu.com",
    packages = find_packages(exclude=["debian", "Makefile", "*.tests", "*.tests.*", "tests.*", "tests", "third"]),
    scripts = ["bin/bae"],
    install_requires = requires,
    zip_safe = False,
    long_description=read('README.txt'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "Programming Language :: Python :: 2 :: Only",
    ],
)
