#!python2
# coding: utf-8

"""
SIMULATOR OF ANTIBIOTIC THERAPY EFFECTS ON THE DYNAMICS OF BACTERIAL POPULATIONS
Program entry point

DEPENDENCIES:
    - Python 2.7
"""

import sys
from bin.ui.ui import start

__author__ = 'Pedro HC David, https://github.com/Kronopt'
__credits__ = ['Pedro HC David']

# log errors
sys.stderr = open('errorlog.txt', 'a')

# run App
start()
